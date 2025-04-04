from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SavingsGoal
from decimal import Decimal

class AppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "testuser@example.com"
        self.password = "securepassword123"

        # ✅ TO‘G‘RI Foydalanuvchi yaratish
        self.user = User.objects.create_user(username=self.email, email=self.email, password=self.password)


    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "email": self.email,
            "password": self.password
        })
        
        self.assertRedirects(response, reverse("home"))

        # ✅ `email` orqali emas, `User` modelidan olish
        user = User.objects.get(email=self.email)
        self.assertEqual(user.email, self.email)


    def test_login_failure(self):
        response = self.client.post(reverse("login"), {
            "email": self.email,
            "password": "wrongpassword"
        })
        self.assertContains(response, "Email yoki parol noto‘g‘ri!")

    def test_logout(self):
        self.client.login(username=self.email, password=self.password)
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_home_authenticated(self):
        self.client.login(username=self.email, password=self.password)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_set_goal(self):
        self.client.login(username=self.email, password=self.password)
        
        response = self.client.post(reverse("set_goal"), {
            "goal_amount": "1000"
        })
        
        self.assertRedirects(response, reverse("add_funds"))

        # ✅ `email` o‘rniga `self.user` ishlatamiz
        goal = SavingsGoal.objects.get(user=self.user)
        
        self.assertEqual(goal.goal_amount, Decimal("1000.00"))
        self.assertEqual(goal.current_amount, Decimal("0.00"))


    def test_add_funds_and_goal_reached(self):
        self.client.login(username=self.email, password=self.password)
        
        # ✅ `user=self.email` EMAS, balki `user=self.user` bo‘lishi kerak
        goal = SavingsGoal.objects.create(user=self.user, goal_amount=Decimal("500"), current_amount=Decimal("450"))
        
        response = self.client.post(reverse("add_funds"), {
            "amount": "50"
        })
        
        goal.refresh_from_db()  # Ma'lumotlar bazasini yangilash
        
        self.assertEqual(goal.current_amount, Decimal("500"))
        self.assertJSONEqual(response.content, {"goal_reached": True})


    def test_register_sends_code(self):
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            response = self.client.post(reverse("register"), {
                "email": "newuser@example.com",
                "password": "test1234"
            })
            self.assertRedirects(response, reverse("verify_code", kwargs={"email": "newuser@example.com"}))
