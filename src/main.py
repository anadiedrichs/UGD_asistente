# src/main.py
import os
from dotenv import load_dotenv
from .agent import build_graph
from .tools import create_knowledge_base

# Cargar las variables de entorno del archivo .env
load_dotenv()

def main():
    # 1. Crear la base de conocimiento si no existe, sino cargarla
    create_knowledge_base()

    # 2. Construir el grafo de LangGraph
    app = build_graph()

    # 3. Iniciar la interacción con el usuario
    print("¡Hola! Soy el asistente de la UGD. ¿En qué puedo ayudarte?")
    while True:
        question = input(">> ")
        if question.lower() in ["salir", "exit"]:
            break
        
        # Invocar el grafo con la pregunta del usuario
        inputs = {"question": question}
        final_state = app.invoke(inputs)
        
        # Mostrar la respuesta final
        print("\nRespuesta del Asistente:")
        print(final_state["generation"])
        print("\n---")


if __name__ == "__main__":
    main()