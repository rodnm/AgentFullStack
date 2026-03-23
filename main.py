import os
from dotenv import load_dotenv
from agent import run_agent

def main():
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY no está configurado en el entorno.")
        return
        
    historial = []
    
    # Crear un directorio temporal para la prueba
    test_dir = os.path.join(os.getcwd(), "astro-todos")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    # Cambiamos el directorio de trabajo para que el agente opnere ahí
    os.chdir(test_dir)
        
    print("\\n" + "="*50)
    print("TAREA 1: Creando app de tareas estilo Windows 95")
    print("="*50)
    
    prompt_1 = "Crea una app de lista de tareas estilo Windows 95 usando Astro y Tailwind. Inicia el proyecto en el directorio actual y asegurate de NO borrar nada. Escribe todos los archivos necesarios de tu aplicacion."
    run_agent(prompt_1, messages=historial)
    
    print("\\n" + "="*50)
    print("TAREA 2: Modificando la app")
    print("="*50)
    
    # Inyectar texto falso masivo en el historial para forzar el límite de tokens y probar compresión
    # 40000 tokens son aprox 160000 caracteres.
    print("[*] Inyectando historial extenso para probar compresión antes de la tarea 2...")
    dummy_text = "texto de relleno para simular una larga conversacion técnica sobre componentes React " * 3000
    historial.insert(1, {
        "role": "model",
        "parts": [{"text": dummy_text}]
    })
    
    prompt_2 = "Los íconos del nav son blancos y no se ven. Arreglalo modificando los archivos actuales."
    run_agent(prompt_2, messages=historial)
    
    print("\\n" + "="*50)
    print("TAREAS COMPLETADAS")
    print("="*50)
    
    # Resumen de historial final
    print(f"Mensajes finales en historial: {len(historial)}")
    
if __name__ == "__main__":
    main()
