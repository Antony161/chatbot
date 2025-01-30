from django.shortcuts import render,redirect
from django.http import JsonResponse
import ollama
import requests
from django.http import JsonResponse
from langchain_ollama import ChatOllama
from llama_index.core import Settings
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
from django.contrib.auth import get_user
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
import json
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
from llama_index.core import StorageContext
from llama_index.core import StorageContext, load_index_from_storage
from pathlib import Path



index_folder="/home/antonyeyyo/django_chatbot/chatbot/index_store"

uploaded_folder="/home/antonyeyyo/django_chatbot/chatbot/uploaded_documents"



def ask_llama_rag(message):
    print("rag")
    Settings.llm=ChatOllama(model="llama3.2",temperature=0.1)
    Settings.embed_model="local:BAAI/bge-small-en-v1.5"
    storage_context = StorageContext.from_defaults(persist_dir="index_store")
    index = load_index_from_storage(storage_context)
    chat_engine = index.as_chat_engine()
    response = chat_engine.chat(message)
    response=str(response)
    return response





# Create your views here
memory=ConversationBufferMemory()
custom_prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=(
       "You are a highly intelligent and context-aware assistant. Your task is to provide accurate, concise, and helpful answers "
        "to the user's questions while leveraging the conversation history to maintain context and continuity.\n\n"
        "Guidelines:\n"
        "1. Carefully review the conversation history to understand the context of the user's current query.\n"
        "2. Refer to previous interactions when relevant to avoid redundant explanations.\n"
        "3. If no relevant context exists in the history, treat the query as standalone and provide the best possible response.\n"
        "4. Be clear, concise, and user-friendly in your answers.\n"
        "5. When summarizing or providing recommendations, ensure they align with the user's stated preferences or goals.\n\n"
        "Here is the conversation so far:\n"
        "{history}\n"
        "User: {input}\n"
        "Assistant:"
    ),
)

API_URL = "http://localhost:11434/api/generate"

def query_model(message):
    payload = {
        "model": "llama3.2",
        "prompt": message,  # Make sure the input parameter matches the expected one
        "stream":False
    }
    print("Payload:", payload)

    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    response=json.loads(response.text)
    return response["response"]

llm=ChatOllama(model="llama3.2",temperature=0.1)
conversation_buf = ConversationChain(
llm=llm,
memory=memory,
prompt=custom_prompt,
)




def chatbot(request):
    user = get_user(request)
    if user.is_anonymous:
        # Handle anonymous user case
        return redirect('register')  # Or some other fallback logic
    chats=Chat.objects.filter(user=request.user)
    if request.method=='POST':
        message=request.POST.get('message')
        # prompt=JsonResponse({"model":"llam3.2:3b",'prompt':message})
        if os.path.exists(index_folder):
            response=ask_llama_rag(message)
        else:
            response=query_model(message)
        chat=Chat(user=request.user,message=message,response=response,created_at=timezone.now())
        chat.save()
        return JsonResponse({'message':message,'response':response})
    return render(request,'chatbot.html',{'chats':chats})


from .forms import DocumentUploadForm
from .models import UploadedDocument
import os 

def upload_document(request):
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)  # Get POST data and uploaded file
        if form.is_valid():
            doc = form.save()  # Save the document to the database and storage
            file_path = os.path.join('uploaded_documents', doc.file.name)  # Get the full file path
            print(f"File saved at: {file_path}")  # Debugging: Check the file path
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

            return redirect('chatbot')  # Redirect to a success page after upload

    else:
        form = DocumentUploadForm()  # Create a new empty form for GET requests
    
    return render(request, 'upload.html', {'form': form})  # Render the form to the user


def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        try:
            user=User.objects.get(username=username)
        except:
            error_message="Invalid user"
            return render(request,'login.html',{'error_message':error_message})
        user=auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message='Incorrect password'
            return render(request,'login.html',{'error_message':error_message})
    else:
        return render(request,'login.html')





from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Check if passwords match
        if password1 != password2:
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists'
            return render(request, 'register.html', {'error_message': error_message})

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            error_message = 'Email already exists'
            return render(request, 'register.html', {'error_message': error_message})

        # Create the user
        try:
            user = User.objects.create_user(username, email, password1)
            user.save()
            auth.login(request, user)
            memory.clear()
            return redirect('chatbot')
        except Exception as e:
            # Handle any unexpected errors
            error_message = f'Error creating account: {str(e)}'
            return render(request, 'register.html', {'error_message': error_message})

    # Render the registration page for GET requests
    return render(request, 'register.html')

def logout(request):
    if os.path.exists(index_folder):
        for file_name in os.listdir(index_folder):
            file_path = os.path.join(index_folder, file_name)
            if os.path.isfile(file_path):  # Check if it's a file
                os.remove(file_path)  # Delete the file
    os.rmdir(index_folder)
    if os.path.exists(uploaded_folder):
        for file_name in os.listdir(uploaded_folder):
            file_path = os.path.join(uploaded_folder, file_name)
            if os.path.isfile(file_path):  # Check if it's a file
                os.remove(file_path)  # Delete the file
    auth.logout(request)

    return redirect('login')