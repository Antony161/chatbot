from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.core import StorageContext
from llama_index.core import StorageContext, load_index_from_storage
from pathlib import Path



# Define the folder path
folder_path = Path("/home/antonyeyyo/django_chatbot/chatbot/uploaded_documents/")

# Get all PDF files in the folder
pdf_files = list(folder_path.glob("*.pdf"))

documents=SimpleDirectoryReader(input_files=[str(file) for file in pdf_files]).load_data()

document=Document(text="\n\n".join([doc.text for doc in documents]))
Settings.embed_model="local:BAAI/bge-small-en-v1.5"

index = VectorStoreIndex.from_documents([document],
                                        service_context=Settings.embed_model)
index.storage_context.persist(persist_dir="index_store")