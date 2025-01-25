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
import json


# Create your views here.

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


def ask_llama(message):
    response=conversation_buf.invoke(message)
    return response



def chatbot(request):
    user = get_user(request)
    if user.is_anonymous:
        # Handle anonymous user case
        return redirect('register')  # Or some other fallback logic
    chats=Chat.objects.filter(user=request.user)
    if request.method=='POST':
        message=request.POST.get('message')
        # prompt=JsonResponse({"model":"llam3.2:3b",'prompt':message})
        response=ask_llama(message)['response']
    
        # response=query_model(message)
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
            memory.clear()
            auth.login(request,user)
            chats=Chat.objects.filter(user=request.user)
            chat_hist=[]
            for chat in chats:
                chat_hist.append(f'User: {chat.message}\nAssistant: {chat.response}')
            if len(chat_hist)>0:
                memory.clear()
                for hist in chat_hist:
                    memory.save_context({"input":hist.split('\n')[0]},{"output":hist.split('\n')[1]})
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
                memory.clear()
                return redirect('chatbot')
                
            except:
                error_message='error creating account'
                return render(request,'register.html',{'error_message':error_message})

        else:
            error_message='password dont match'
            return render(request,'register.html',{'error_message':error_message})
    return render(request,'register.html')

def logout(request):
    memory.clear()
    auth.logout(request)
    return redirect('login')