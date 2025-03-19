from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings
import random


verification_codes = {}

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        verification_code = str(random.randint(100000, 999999))
        verification_codes[email] = {"code": verification_code, "password": password}
        
        send_mail(
            "Email tasdiqlash kodi",
            f"Sizning tasdiqlash kodingiz: {verification_code}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        return redirect("verify_code", email=email)
    
    return render(request, "register.html")

def verify_code(request, email):
    if request.method == "POST":
        entered_code = request.POST.get("code")

        if email in verification_codes and verification_codes[email]["code"] == entered_code:
            password = verification_codes[email]["password"]
            user, created = User.objects.get_or_create(username=email, email=email)
            user.set_password(password)
            user.save()
            login(request, user)

            del verification_codes[email] 
            return redirect("success")  

        else:
            return render(request, "verify_code.html", {"email": email, "error": "Kod noto‘g‘ri!"})

    return render(request, "verify_code.html", {"email": email})
