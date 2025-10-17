import os
from typing import TypedDict, List
from langchain_core.prompts import ChatPromptTemplate
# Importa el modelo de chat de Google (Gemini)
from langchain_google_genai import ChatGoogleGenerativeAI 
from langgraph.graph import StateGraph, END
# Importa las herramientas necesarias de tools.py
from .tools import get_retriever, save_to_notion

# --- 1. Definición del Estado del Grafo ---
class GraphState(TypedDict):
    question: str
    documents: List[str]
    generation: str
    sources: List[str]

# --- 2. Definición de los Nodos (Agentes) ---

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

def generate_response(state):
    """
    Nodo 2: "Redactor Empático UGD".
    Genera una respuesta usando el modelo Gemini.
    """
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
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", 
                                 temperature=0, 
                                 api_key=api_key)
    chain = prompt | llm
    
    generation = chain.invoke({"context": "\n\n".join(documents), "question": question}).content
    return {"generation": generation}

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