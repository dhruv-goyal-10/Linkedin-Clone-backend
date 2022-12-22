from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import datetime

class UserManager(BaseUserManager):
    def create_user(self, email,password=None):
        
        if not email:
            raise ValueError('Users must have an email address')
        
        if not password:
            raise ValueError('Users must have a Password')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
    
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


#  Custom User Model

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def is_Active(self):
        return self.is_active
    
    @property
    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        refresh['email'] = self.email
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
class PhoneOTP(models.Model):
    
    phone_number = models.BigIntegerField(unique=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.phone_number}"
    
    class Meta:
        verbose_name_plural = 'Phone OTPs'

    
class EmailOTP(models.Model):
    
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    
    otp = models.IntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.email}"
    
    class Meta:
        verbose_name_plural = 'Email OTPs'

    
    
    