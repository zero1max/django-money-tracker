from django.urls import path
from django.shortcuts import render
from .views import register, verify_code

urlpatterns = [
    path("register/", register, name="register"),
    path("verify/<str:email>/", verify_code, name="verify_code"),
    path("success/", lambda request: render(request, "success.html"), name="success"),
]