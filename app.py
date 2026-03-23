import os
import gradio as gr
from dotenv import load_dotenv
from google import genai
from agent import run_agent_stream

load_dotenv()

client = None

def chat(message, history, state_messages):
    global client
    if not client:
        # Inicializar solo si hay Key, lo cual idealmente se pide al iniciar o la saca de env
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            yield "⚠️ Error: Falta GEMINI_API_KEY en tu entorno o archivo .env"
            return
        client = genai.Client(api_key=api_key)
        
    if state_messages is None:
        state_messages = []
        
    response_stream = ""
    for status, new_state in run_agent_stream(message, state_messages, client):
        response_stream += f"\\n{status}"
        yield response_stream
        
    return response_stream

with gr.Blocks(title="Full Stack Agent") as demo:
    gr.Markdown("# 🤖 Agente de Código Full Stack")
    gr.Markdown("Pídele al agente que construya tu aplicación. Abrirá la carpeta `astro-todos-ui` y programará allí los archivos.")
    
    # Hidden state to store actual Gemini dictionary formats correctly
    state = gr.State([])
    
    chatbot = gr.ChatInterface(
        fn=chat,
        additional_inputs=[state],
        title="Agent Terminal",
        description="El agente te irá reportando en tiempo real las herramientas que utiliza y el razonamiento del modelo."
    )

if __name__ == "__main__":
    # Create the test directory to isolate executions by default
    test_dir = os.path.join(os.getcwd(), "astro-todos-ui")
    os.makedirs(test_dir, exist_ok=True)
    os.chdir(test_dir)
    print(f"[*] Carpeta de trabajo establecida en: {test_dir}")
    demo.launch()
