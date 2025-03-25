from django.urls import path
from django.shortcuts import render
from .views import register, verify_code, set_goal, add_funds, user_login, user_logout

urlpatterns = [
    path("", user_login, name="login"),
    path("register/", register, name="register"),
    path("verify/<str:email>/", verify_code, name="verify_code"),
    path("logout/", user_logout, name="logout"),
    path("success/", lambda request: render(request, "success.html"), name="success"),
    path("set_goal/", set_goal, name="set_goal"),
    path("add_funds/", add_funds, name="add_funds"),
]