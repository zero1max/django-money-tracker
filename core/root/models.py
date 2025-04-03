from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
#
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE = (
        ('User', 'user'),
        ('Admin', 'admin')
    )
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)



class SavingsGoal(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    all_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def is_goal_reached(self):
        return self.current_amount >= self.goal_amount
