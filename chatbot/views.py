from django.shortcuts import render,redirect
from django.http import JsonResponse
import ollama
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
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings


# Create your views here.


documents=SimpleDirectoryReader(input_files=[
    "/home/guest/django_project2/django_chatbot/context.txt"
]).load_data()

document=Document(text="\n\n".join([doc.text for doc in documents]))
Settings.embed_model="local:BAAI/bge-small-en-v1.5"

index = VectorStoreIndex.from_documents([document],
                                        service_context=Settings.embed_model)


Settings.llm=ChatOllama(model="llama3.2:3b",temperature=0.1)
query_engine = index.as_query_engine()

def ask_llama(message):
    response = query_engine.query(message)
    response=str(response)
    return response



def chatbot(request):
    user = get_user(request)
    if user.is_anonymous:
        # Handle anonymous user case
        return redirect('register')  # Or some other fallback logic
    chats=Chat.objects.filter(user=request.user)
    if request.method=='POST':
        message=request.POST.get('message')
        response=ask_llama(message)
        chat=Chat(user=request.user,message=message,response=response,creared_at=timezone.now())
        chat.save()
        return JsonResponse({'message':message,'response':response})
    return render(request,'chatbot.html',{'chats':chats})



def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message='Invalid user'
            return render(request,'register.html',{'error_message':error_message})
    else:
        return render(request,'login.html')





def register(request):
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password1']
        password2=request.POST['password2']

        if password1==password2:
            try:
                user=User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
                
            except:
                error_message='error creating account'
                return render(request,'register.html',{'error_message':error_message})

        else:
            error_message='password dont match'
            return render(request,'register.html',{'error_message':error_message})
    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')