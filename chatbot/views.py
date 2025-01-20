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
# Create your views here.


def ask_llama(message):
    llm=ChatOllama(model="llama3.2:1b",temperature=0.1)
    response =llm.invoke((message))
    response=response.content
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