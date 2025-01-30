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
<<<<<<< HEAD
from langchain_community.embeddings import OllamaEmbeddings
from llama_index.core import SimpleDirectoryReader
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings
=======
import json
>>>>>>> f362d36


# Create your views here.

<<<<<<< HEAD
=======
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
# API_KEY="LA-9d8ef9653cd14e4bab1becd540f9396a3dd2daba3ba649dca926ca4cbeb750c1"

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
    # try:
    #     response_parts = response.text.strip().split('\n')

    #     parsed_responses = []
    #     for part in response_parts:
    #         try:
    #             response_json = json.loads(part)  # Parse each part as JSON                # You can collect and process individual responses here
    #             response_part = response_json.get("response", "")
    #             parsed_responses.append(response_part)
    #         except json.decoder.JSONDecodeError as e:
    #             print(f"Error decoding JSON part: {e}")
        
    #     full_response = " ".join(parsed_responses)
    #     return full_response

    # except Exception as e:
    #     print("General Error:", e)
    #     return f"An error occurred: {e}"

llm=ChatOllama(model="llama3.2",temperature=0.1)
conversation_buf = ConversationChain(
llm=llm,
memory=memory,
prompt=custom_prompt,
)
>>>>>>> f362d36

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
<<<<<<< HEAD
    response = query_engine.query(message)
    response=str(response)
=======
    response=conversation_buf.invoke(message)
>>>>>>> f362d36
    return response



def chatbot(request):
    user = get_user(request)
    if user.is_anonymous:
        # Handle anonymous user case
        return redirect('register')  # Or some other fallback logic
    chats=Chat.objects.filter(user=request.user)
    new_session = request.session.pop('session', False)
    session_id = request.session.get('session_id')
    print(session_id)
    if request.method=='POST':
        message=request.POST.get('message')
        # prompt=JsonResponse({"model":"llam3.2:3b",'prompt':message})
        response=ask_llama(message)['response']
        # response=query_model(message)
        chat=Chat(user=request.user,message=message,response=response,created_at=timezone.now(),session_id=session_id)
        chat.save()
        return JsonResponse({'message':message,'response':response})
    return render(request,'chatbot.html',{'chats':chats,'new_session': new_session})


import uuid

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
            session_id = str(uuid.uuid4())
            request.session['session']=True
            request.session['session_id'] = session_id
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

<<<<<<< HEAD
        if password1==password2:
            try:
                user=User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
                
            except:
                error_message='error creating account'
                return render(request,'register.html',{'error_message':error_message})
=======
        # Check if passwords match
        if password1 != password2:
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})
>>>>>>> f362d36

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
    auth.logout(request)
    return redirect('login')