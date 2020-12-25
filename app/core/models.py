from django.db import models
from django.contrib.auth.models import  AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """sreate and saves a new user """
        user=self.model(email=self.normalize_email(email), **extra_fields)
        if not email:
            raise ValueError('user must have email adres')
        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_superuser(self, email, password):
        """creates and saves new superuser"""
        user = self.create_user(email, password)
        user.is_staff =True
        user.is_superuser = True
        user.save(using=self._db)

        return user
class User(AbstractBaseUser, PermissionsMixin):
    """custom user model that suports email insted of username"""
    email= models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff= models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """tag to be used for a recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """ingredient to be userd in recipe"""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,)

    def __str__(self):
        return self.name