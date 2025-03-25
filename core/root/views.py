from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from .models import SavingsGoal
from decimal import Decimal
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


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("set_goal")  
        else:
            return render(request, "login.html", {"error": "Email yoki parol noto‘g‘ri!"})

    return render(request, "login.html")


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def set_goal(request):
    if request.method == "POST":
        goal_amount = request.POST.get("goal_amount")
        SavingsGoal.objects.update_or_create(
            user=request.user,
            defaults={"goal_amount": goal_amount, "current_amount": 0},
        )
        return redirect("add_funds")

    return render(request, "set_goal.html")


@login_required
def add_funds(request):
    goal = SavingsGoal.objects.filter(user=request.user).first()

    if request.method == "POST":
        amount = request.POST.get("amount")

        if goal:
            goal.current_amount += Decimal(amount)
            goal.save()

            if goal.is_goal_reached():
                send_mail(
                    "Maqsadga yetdingiz!",
                    f"Tabriklaymiz! Siz belgilangan {goal.goal_amount} summani yig‘dingiz!",
                    settings.EMAIL_HOST_USER,
                    [request.user.email],
                    fail_silently=False,
                )

        return redirect("add_funds")

    return render(request, "add_funds.html", {"goal": goal})
