import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from decimal import Decimal
from .models import SavingsGoal  # O'z model faylingizga moslashtiring

# Faol User modelini olish
User = get_user_model()

# pytest uchun fixture'lar
@pytest.fixture
def client():
    from django.test import Client
    return Client()

@pytest.fixture
def user(db):
    email = "testuser@example.com"
    password = "securepassword123"
    return User.objects.create_user(username=email, email=email, password=password)

@pytest.mark.django_db
def test_login_success(client, user):
    email = "testuser@example.com"
    password = "securepassword123"
    
    response = client.post(reverse("login"), {
        "email": email,
        "password": password
    })
    
    assert response.status_code == 302  # Redirect
    assert response.url == reverse("home")
    
    user_db = User.objects.get(email=email)
    assert user_db.email == email

@pytest.mark.django_db
def test_login_failure(client, user):
    response = client.post(reverse("login"), {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    })
    
    assert "Email yoki parol noto‘g‘ri!" in response.content.decode()

@pytest.mark.django_db
def test_logout(client, user):
    client.login(username=user.email, password="securepassword123")
    response = client.get(reverse("logout"))
    
    assert response.status_code == 302
    assert response.url == reverse("login")

@pytest.mark.django_db
def test_home_authenticated(client, user):
    client.login(username=user.email, password="securepassword123")
    response = client.get(reverse("home"))
    
    assert response.status_code == 200
    assert "home.html" in [t.name for t in response.templates]

@pytest.mark.django_db
def test_set_goal(client, user):
    client.login(username=user.email, password="securepassword123")
    
    response = client.post(reverse("set_goal"), {
        "goal_amount": "1000"
    })
    
    assert response.status_code == 302
    assert response.url == reverse("add_funds")
    
    goal = SavingsGoal.objects.get(user=user)
    assert goal.goal_amount == Decimal("1000.00")
    assert goal.current_amount == Decimal("0.00")

@pytest.mark.django_db
def test_add_funds_and_goal_reached(client, user):
    client.login(username=user.email, password="securepassword123")
    
    goal = SavingsGoal.objects.create(user=user, goal_amount=Decimal("500"), current_amount=Decimal("450"))
    
    response = client.post(reverse("add_funds"), {
        "amount": "50"
    })
    
    goal.refresh_from_db()
    
    assert goal.current_amount == Decimal("500")
    assert response.json() == {"goal_reached": True}

@pytest.mark.django_db
def test_register_sends_code(client, settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    
    response = client.post(reverse("register"), {
        "email": "newuser@example.com",
        "password": "test1234"
    })
    
    assert response.status_code == 302
    assert response.url == reverse("verify_code", kwargs={"email": "newuser@example.com"})