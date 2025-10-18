
# ___Cabeza del Agente___
'''
    Este .py define la lógica del flujo de trabajo, para saber 
    cuál va a ser el camino a seguir para la pregunta desde que 
    se recibe hasta que el agente genera una respuesta.
    Aquí LangGraph se utiliza para secuenciar las acciones del agente digital.
'''
import os
from typing import List, TypedDict
from langchain_core.prompts import ChatPromptTemplate

# Importa el modelo de chat de Google (Gemini)
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

# Importa las herramientas necesarias de tools.py
from .tools import get_retriever, save_to_notion


# --- 1. Definición del Estado del Grafo ---
'''
    La siguiente clase 'GraphState' funciona como 'almacenamiento de memoria'
    que comparte información entre los agentes
'''
class GraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    sources: List[str]

# --- 2. Definición de los Nodos (Agentes) ---

'''
    La siguiente función 'retrieve_documents' funciona como un 'Agente Buscador'
    el cual para buscar documentos utilizar 'get_retriever' (definida en tools.py)
    para buscar en la base de conocimiento los fragmentos de texto más relevantes para la pregunta.

    Retorna la lista de documentos y fuentes encontradas al estado.

'''
def retrieve_documents(state):
    print("---Buscando documentos relevantes---")
    question = state["question"]
    retriever = get_retriever()
    docs = retriever.invoke(question)
    documents = [d.page_content for d in docs]
    sources = [d.metadata.get('source', 'N/A') for d in docs]
    print("---Documentos encontrados---")
    print(documents)
    return {"documents": documents, "question": question, "sources": list(set(sources))}


'''
    La siguiente función 'generate_response' funciona como un 
    ' Agente Redactor Empático de la Unidad de Género y Diversidad '
    el cual toma la pregunta y los documentos para combinar en un prompt para el modelo de IA.
    El modelo de IA utilizado es Gemini 2.5 Flash de Google. 
    El modelo se configura como un asistente empático que únicamente
    responde con el contexto proporcionado y debe citar las fuentes.

    Retorna la respuesta generada al estado.

'''
def generate_response(state):
    print("---Generando respuesta---")
    question = state["question"]
    documents = state["documents"]
    
    prompt = ChatPromptTemplate.from_template(
        """Eres un asistente virtual para la Unidad de Género y Diversidad de la UTN Mendoza.
        Tu misión es responder preguntas de forma clara, empática y basada únicamente en la información proporcionada.
        No inventes nada. Si la información no es suficiente, indica que no puedes responder con los datos disponibles.
        Cita siempre tus fuentes al final de la respuesta.

        Contexto (documentos oficiales):
        {context}

        Pregunta del usuario:
        {question}

        Respuesta:
        """
    )

    # Carga la API key desde el entorno y pasarla explícitamente
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GEMINI_API_KEY no fue encontrada.")
        
    # Usa el modelo de chat de Gemini
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=api_key)
    chain = prompt | llm
        
    generation = chain.invoke({"context": "\n\n".join(documents), "question": question}).content
    return {"generation": generation}


'''
    La siguiente función 'persist_report' funciona como un ' Agente Documentador'
    el cual utiliza la herramienta 'save_to_notion' (definida en tools.py)
    para guardar toda la interacción completa en la BD de Notion.
'''
def persist_report(state):
    
    print("---Guardando en Notion---")
    save_to_notion(
        query=state["question"],
        response=state["generation"],
        sources=", ".join(state["sources"]),
        category="Protocolo" #TODO hacer dinámico esto, quizás con otro nodo previo.
    )
    return {}

# --- 3. Construcción del Grafo 

'''
    La Funcion 'build_graph' es la encargada de ensamblar a los agentes para generar el flujo de trabajo.
    Inicializo el flujo de trabajo llamando a 'StateGraph' y utilizando la definición de 'GraphState'. 
    Agrego las 3 subrutinas al flujo de trabajo. 

    Retorna la secuencia lineal: retrieve -> generarte -> persist -> END.
'''
def build_graph():
    
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("generate", generate_response)
    workflow.add_node("persist", persist_report)
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    # workflow.add_edge("generate", END)
    workflow.add_edge("generate", "persist")
    workflow.add_edge("persist", END)
    app = workflow.compile()
    return app
