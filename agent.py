import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

from typing import List, Dict, Any, Optional

from lib.sbx_tools import (
    list_directory,
    read_file,
    write_file,
    search_file_content,
    replace_in_file,
    glob_search,
    ToolError
)

MAX_TOKENS = 40_000
COMPRESSION_RATIO = 0.70

SYSTEM_PROMPT_WEB_DEV = """
You are an expert Full Stack Web Developer specializing in Astro, React, and TailwindCSS.
Your goal is to build web applications directly on the user's local file system.
You understand Islands Architecture, static/hybrid rendering, and how to create a pristine user experience.

Instructions:
1. Always think step-by-step. Let the user's prompt guide your actions.
2. Formulate your solution and break it down.
3. If initiating a new project, use terminal commands (if available) or create the necessary files. Since standard tools provided give you file writing capabilities, you should write complete files.
4. DO NOT leave placeholders like '/* add your code here */'. Write fully functional, production-ready code.
5. Apply Astro components and use React components only when client-side state is required (use `client:load` or `client:idle`).
6. Apply TailwindCSS for styling and ensure accessibility (a11y) best practices are maintained.
7. Important: Make sure interfaces are visually rich, addressing any specific style requirements (e.g. Windows 95 style).

Workflow:
- Use `list_directory` to explore current files.
- Use `write_file` to create or overwrite fully implemented files.
- Use `replace_in_file` to make targeted modifications.
- Use `search_file_content` to find specific code.
- When done, report the completion to the user clearly.
"""

def count_tokens(messages: List[Dict]) -> int:
    """Estimates token count for local fast checking. 
    1 token is approximately 4 characters."""
    total_chars = 0
    for m in messages:
        text = ""
        if "parts" in m:
            for p in m["parts"]:
                if "text" in p:
                    text += p["text"]
                elif "function_call" in p:
                    # just a rough approximation for function calls
                    text += str(p["function_call"])
                elif "function_response" in p:
                    text += str(p["function_response"])
        total_chars += len(text)
    return max(1, total_chars // 4)

def compress_context(messages: List[Dict], client: genai.Client) -> List[Dict]:
    """Compresses the oldest 70% of messages into a single summary to fit within limits."""
    total_msgs = len(messages)
    if total_msgs <= 2:
        return messages # Too few to compress
        
    split_index = int(total_msgs * COMPRESSION_RATIO)
    
    old_messages = messages[:split_index]
    recent_messages = messages[split_index:]
    
    # Format old messages for summarization
    content_to_summarize = "Please summarize the following conversation history. Retain all technical decisions, file changes, and instructions to ensure no context is lost.\\n\\n"
    for m in old_messages:
        role = m.get("role", "user")
        text = ""
        if "parts" in m:
            for p in m["parts"]:
                if "text" in p:
                    text += p["text"]
                elif "function_call" in p:
                    text += f"[Tool Call: {p['function_call']['name']}] "
                elif "function_response" in p:
                    text += f"[Tool Response: {p['function_response']['name']}] "
        content_to_summarize += f"{role.upper()}: {text}\\n\\n"
        
    print(f"[*] Compressing {len(old_messages)} messages...")
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=content_to_summarize
            )
            summary_text = response.text
            break
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"[!] Compression rate limit hit. Waiting 15s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(15)
            else:
                print(f"[!] Compression failed: {e}")
                return messages # fallback
    else:
        print("[!] Compression failed after max retries")
        return messages
        
    summary_message = {
        "role": "model",
        "parts": [{"text": f"Context Summary of previous interactions:\\n{summary_text}"}]
    }
    
    return [summary_message] + recent_messages

def maybe_compress(messages: List[Dict], client: genai.Client) -> List[Dict]:
    tokens = count_tokens(messages)
    if tokens > MAX_TOKENS:
        print(f"[*] Token limit exceeded ({tokens} > {MAX_TOKENS}). Initiating compression...")
        return compress_context(messages, client)
    return messages

def get_tool_declarations(available_tools):
    """Generates the SDK format tool declarations dynamically from python functions."""
    tool_list = []
    
    for name, func in available_tools.items():
        # Get parameter names from code inspection for a very basic schema
        import inspect
        sig = inspect.signature(func)
        properties = {}
        required = []
        for param_name, param in sig.parameters.items():
            properties[param_name] = {"type": "STRING", "description": f"Parameter {param_name}"}
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
                
        # Manually fine tune if int type expected (only search_file_content has int for max_results)
        if name == "search_file_content":
            properties["max_results"] = {"type": "INTEGER", "description": "max results to return"}
            
        tool_list.append(types.FunctionDeclaration(
            name=name,
            description=func.__doc__ or f"Function {name}",
            parameters={
                "type": "OBJECT",
                "properties": properties,
                "required": required
            }
        ))
    return [types.Tool(function_declarations=tool_list)]

def run_agent_stream(prompt: str, messages: List[Dict], client: genai.Client = None):
    if not client:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
    messages.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })
    
    messages = maybe_compress(messages, client)
    
    available_tools = {
        "list_directory": list_directory,
        "read_file": read_file,
        "write_file": write_file,
        "search_file_content": search_file_content,
        "replace_in_file": replace_in_file,
        "glob_search": glob_search
    }
    
    tool_declarations = get_tool_declarations(available_tools)

    yield "Pensando...", messages
    import time
    
    while True:
        try:
            gemini_messages = []
            for m in messages:
                parts = []
                for p in m["parts"]:
                    if "text" in p:
                        parts.append(types.Part.from_text(text=p["text"]))
                    elif "function_call" in p:
                        args = {k: v for k,v in p["function_call"]["args"].items()}
                        parts.append(types.Part.from_function_call(
                            name=p["function_call"]["name"],
                            args=args
                        ))
                    elif "function_response" in p:
                        parts.append(types.Part.from_function_response(
                            name=p["function_response"]["name"],
                            response=p["function_response"]["response"]
                        ))
                gemini_messages.append(types.Content(role=m.get("role", "user"), parts=parts))

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=gemini_messages,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT_WEB_DEV,
                    tools=tool_declarations,
                    temperature=0.2
                )
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                yield "Límite de API alcanzado. Esperando 15s...", messages
                time.sleep(15)
                continue
            else:
                yield f"[!] Error conectando a Gemini: {error_str}", messages
                break

        model_message = {"role": "model", "parts": []}
        agent_text = ""
        if response.text:
            model_message["parts"].append({"text": response.text})
            agent_text = response.text
            
        function_calls = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)
                    args_dict = dict(part.function_call.args)
                    model_message["parts"].append({
                        "function_call": {
                            "name": part.function_call.name,
                            "args": args_dict
                        }
                    })
                    
        messages.append(model_message)
        
        if not function_calls:
            if agent_text:
                yield f"**Agente**: {agent_text}", messages
            break
            
        if agent_text:
            yield f"**Agente**: {agent_text}", messages
            
        tool_responses = []
        for fc in function_calls:
            name = fc.name
            args = dict(fc.args)
            yield f"🔨 Ejecutando `{name}`...", messages
            
            if "max_results" in args and isinstance(args["max_results"], float):
                args["max_results"] = int(args["max_results"])
            
            result_str = ""
            try:
                if name in available_tools:
                    result = available_tools[name](**args)
                    result_str = str(result)
                else:
                    result_str = f"Error: Tool '{name}' not found."
            except ToolError as e:
                result_str = str(e)
            except Exception as e:
                result_str = f"Unexpected Error evaluating {name}: {str(e)}"
                
            tool_responses.append({
                "function_response": {
                    "name": name,
                    "response": {"result": result_str}
                }
            })
            
            yield f"✓ `{name}` finalizado.", messages
            
        messages.append({
            "role": "user",
            "parts": tool_responses
        })
        
        messages = maybe_compress(messages, client)

def run_agent(prompt: str, messages: List[Dict], client: genai.Client = None):
    # Wrapper para retrocompatibilidad con scripts (como main.py) no streamings
    for status, msgs in run_agent_stream(prompt, messages, client):
        print(status)
        messages.clear()
        messages.extend(msgs)

