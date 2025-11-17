# src/main.py
'''
    ​Este es el archivo principal que ejecuta el programa y maneja la interacción con el usuario.
'''   
import os
from dotenv import load_dotenv
from .agent import build_graph
from .tools import create_knowledge_base

# Cargar las variables de entorno del archivo .env
'''
    La función load_dotenv() carga claves API y otras configuraciones desde el archivo .env.
'''    
load_dotenv()

def main():
    # 1. Crear la base de conocimiento si no existe, sino cargarla
    '''
        La función create_knowledge_base() se asegura de que la base de datos vectorial esté lista.
        Si no existe, la crea y si ya existe, la carga.
    '''   
    create_knowledge_base()

    # 2. Construir el grafo de LangGraph
    ''' 
        La funcion build_graph() carga el flujo de trabajo definido en agent.py.
    '''
    app = build_graph()

    # 3. Iniciar la interacción con el usuario
    print("¡Hola! Soy el asistente de la UGD. ¿En qué puedo ayudarte?")
    '''
        El bucle de Interacción:
        ​1_Le pide al usuario que ingrese una question.
        2_​Si el usuario escribe "salir" o "exit", el programa termina.
        3_​app.invoke(inputs) ejecuta el grafo de estados con la pregunta.
        4_​Muestra la respuesta al usuario.
    '''
    
    while True:
        question = input(">> ")
        
        # Eliminar espacios en blanco al inicio y final
        question = question.strip()
        
        if question.lower() in ["salir", "exit"]:
            break
        
        # Verificar si el input está vacío después de strip()
        if not question:
            print("⚠️  Por favor, escribe una pregunta válida.\n")
            continue
        
        # Invocar el grafo con la pregunta del usuario
        inputs = {"question": question}
        final_state = app.invoke(inputs)
        
        # Mostrar la respuesta final
        print("\nRespuesta del Asistente:")
        print(final_state["generation"])
        print("\n---")


if __name__ == "__main__":
    main()
