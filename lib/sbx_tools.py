import os
import glob
from typing import List

class ToolError(Exception):
    """Exception raised for errors in the tool executions."""
    pass

def list_directory(path: str) -> str:
    """Lista archivos y carpetas en un directorio especificado.
    
    Args:
        path: La ruta absoluta o relativa al directorio.
    """
    try:
        entries = os.listdir(path)
        return "\n".join(entries) if entries else "Empty directory"
    except Exception as e:
        raise ToolError(f"Error listing directory '{path}': {str(e)}")

def read_file(path: str) -> str:
    """Lee y devuelve el contenido de un archivo de texto.
    
    Args:
        path: La ruta al archivo.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise ToolError(f"Error reading file '{path}': {str(e)}")

def write_file(path: str, content: str) -> str:
    """Escribe contenido en un archivo, creando directorios padre si es necesario.
    
    Args:
        path: La ruta al archivo.
        content: El texto a escribir.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File successfully written to {path}"
    except Exception as e:
        raise ToolError(f"Error writing to file '{path}': {str(e)}")

def search_file_content(pattern: str, search_path: str = ".", max_results: int = 50) -> str:
    """Busca un patrón en el contenido de los archivos iterando sobre el directorio.
    
    Args:
        pattern: El patrón de búsqueda regex.
        search_path: El directorio donde buscar.
        max_results: Número máximo de ocurrencias a retornar.
    """
    import re
    results = []
    try:
        for root, dirs, files in os.walk(search_path):
            # Skip hidden dirs and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            for file in files:
                if file.startswith('.'):
                    continue
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f):
                            if re.search(pattern, line):
                                results.append(f"{filepath}:{i+1}:{line.strip()}")
                                if len(results) >= max_results:
                                    return "\n".join(results)
                except UnicodeDecodeError:
                    pass # Ignore binary
                except Exception:
                    pass
        return "\n".join(results) if results else "No matches found."
    except Exception as e:
        raise ToolError(f"Error searching pattern '{pattern}': {str(e)}")

def replace_in_file(path: str, old: str, new: str) -> str:
    """Lee el archivo, reemplaza 'old' por 'new' textualmente y guarda los cambios.
    
    Args:
        path: Ruta al archivo.
        old: Texto a buscar.
        new: Texto para reemplazar.
    """
    try:
        content = read_file(path)
        if old not in content:
            return f"Error: Old text not found in {path}"
        
        new_content = content.replace(old, new)
        write_file(path, new_content)
        return f"Successfully replaced text in {path}"
    except Exception as e:
        raise ToolError(f"Error replacing text in '{path}': {str(e)}")

def glob_search(pattern: str) -> str:
    """Busca archivos por patrón usando glob (ej. '**/*.js').
    
    Args:
        pattern: El patrón de búsqueda.
    """
    try:
        files = glob.glob(pattern, recursive='**' in pattern)
        return "\n".join(files) if files else "No matches found."
    except Exception as e:
        raise ToolError(f"Error executing glob for pattern '{pattern}': {str(e)}")
