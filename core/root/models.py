from django.db import models
from django.contrib.auth.models import User

class SavingsGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Maqsad summa
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Hozircha yig‘ilgan summa

    def is_goal_reached(self):
        return self.current_amount >= self.goal_amount
