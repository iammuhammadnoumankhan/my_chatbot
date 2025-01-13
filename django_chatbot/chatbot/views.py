from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from .models import Chat
from django.contrib.auth.models import User
from llama_index.llms.openai import OpenAI
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import os
from django.utils import timezone

load_dotenv()

import markdown

def convert_markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

def ask_ai(message):
    provider = os.getenv('PROVIDER')
    base_url = os.getenv('OPENAI_BASE_URL')
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('MODEL')
    temperature = os.getenv('TEMPERATURE')

    if provider == 'groq':
        llm = Groq(model=model, 
                api_key=api_key,
                base_url=base_url,
                temperature=temperature
        )
    elif provider == 'openai':
        llm = OpenAI(
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=temperature,
        )
    else:
        error = "Select a correct provider"
        print(error)
        JsonResponse({'message':message,'response': error})

    response = llm.complete(message)

    return response.text

# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = convert_markdown_to_html(ask_ai(message))

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message':message,'response': response})
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid credentials'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password_confirm = request.POST.get('password2')

        if password == password_confirm:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error Creating Account'
                return render(request, 'login.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')