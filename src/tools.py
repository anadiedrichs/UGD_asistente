# ___Herramientas del proyecto___
'''
    Este .py contiene las funciones de soporte que permiten al 
    agente interactuar. Se crea la base de conocimiento vectorial (FAISS)
    y la base de datos de auditoría (Notion)
'''
import datetime
import os

# dotenv para cargar variables de entorno
from dotenv import find_dotenv, load_dotenv
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
# Importa la clase de embeddings de Google
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# para los embeddings locales con Hugging Face
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# notion
from notion_client import Client

'''
    La siguiente función 'create_knowledge_base' es la encargada de crear
    la base de conocimiento usando un modelo de embedding local
    de Hugging Face. La cual carga documentos cruciales para el
    funcionamiento del Agente Digital

'''
def create_knowledge_base():
    db_path = "faiss_index"
    if not os.path.exists(db_path):
        print("Creando la base de conocimiento con modelo local...")
        
        # --- Carga y división de documentos (esto no cambia) ---
        print("Creando la base de conocimiento...")
        urls = [
            "https://www.argentina.gob.ar/normativa/nacional/ley-27499-318666/texto", # ley Micaela
        ]
        pdf_paths = ["docs/1795.pdf","docs/2066.pdf","docs/sitio-web-frm-utn-contenido.pdf"]  # rutas a los archivos PDF locales

        loaders = [WebBaseLoader(url) for url in urls] + [PyPDFLoader(path) for path in pdf_paths]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())

        #TODO limpiar documentos (quitar headers, footers, \n etc)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # 1. Definimos el modelo que vamos a usar de Hugging Face.
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        # 2. Creamos la instancia de los embeddings.
        #    La primera vez que ejecutes esto, el modelo se descargará automáticamente.
        #    Puede tardar un par de minutos dependiendo de tu conexión.
        print(f"Cargando el modelo de embedding local: {model_name}...")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        print("Modelo cargado. Creando la base de datos vectorial...")

        # 3. Creamos el vectorstore. Ahora todo el proceso es 100% local.
        vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
        vectorstore.save_local(db_path)
        print("¡Base de conocimiento creada y guardada exitosamente!")
    else:
        print("La base de conocimiento ya existe. No se realizaron cambios.")


'''
    La siguiente función 'get_retriever' carga la base de conocimiento
    y el modelo de embedding local.
    Usamos 'paraphrase-multilingual-MiniLM-L12-v2' de Hugging Face, 
    pues es bueno, bonito y barato.

    Retorna un objeto retriever listo para usarse en un RAG.
'''
def get_retriever():

    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever()


'''
    La siguiente función 'get_timestamp' formatea la fecha y hora a un formato ISO 8601,
    ajustado a la zona horaria UTC-3, ya que es el formato que la API de Notion
    necesita para los campos de tipo Date.
'''
def get_timestamp():
    
    # 1. Crear un objeto de zona horaria para UTC-3
    zona_horaria_utc_menos_3 = datetime.timezone(datetime.timedelta(hours=-3))

    # 2. Obtener la fecha y hora actual EN esa zona horaria
    fecha_hora_actual = datetime.datetime.now(tz=zona_horaria_utc_menos_3)

    # 3. Convertir a formato ISO 8601 (esto genera el string exacto que Notion necesita)
    fecha_iso_formateada = fecha_hora_actual.isoformat()

    return fecha_iso_formateada




#  Herramienta de Persistencia en Notion
'''
    La siguiente función ‘save_to_notion’ es la encargada de registrar cada interacción
    en una base de datos de Notion para auditoria. Como herramientas usa el cliente de notion
    ‘notion_client’ y requiere 2 variables de entorno como lo son ‘NOTION_API_KEY’ y ‘NOTION_DATEBASE_ID’

    Almacena la query, response, sources y la category de la consulta.
'''
def save_to_notion(query: str, response: str, sources: str, category: str):
    notion = Client(auth=os.getenv("NOTION_API_KEY"))
    database_id = os.getenv("NOTION_DATABASE_ID")
    fecha_iso_formateada = get_timestamp()
    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Consulta Anónima": {"title": [{"text": {"content": query}}]},

                # Estas son columnas "Text" (que usan rich_text en la API)
                "Respuesta Generada": {"rich_text": [{"text": {"content": response}}]},
                "Fuentes Utilizadas": {"rich_text": [{"text": {"content": sources}}]},

                # Estas ya estaban correctas
                "Fecha de Consulta": {"date": {"start": fecha_iso_formateada}},
                "Categoría": {"select": {"name": category}},
            }
        )
        return "Informe guardado en Notion exitosamente."
    except Exception as e:
        print(f"Error al guardar en Notion: {e}")
        return "Error al guardar el informe en Notion."








# Bloque de prueba para ejecutar este archivo directamente
if __name__ == "__main__":
    print("Ejecutando prueba de tools.py...")
    # Carga las variables desde el archivo .env que está en la raíz del proyecto
    load_dotenv(find_dotenv())

    create_knowledge_base()

    print("Prueba finalizada.")

