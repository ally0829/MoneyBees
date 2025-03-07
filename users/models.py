from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email),
                          firstname=firstname, lastname=lastname)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        user = self.create_user(email, firstname, lastname, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model that replaces Django's default auth.User"""
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=128)
    lastname = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    currency = models.ForeignKey(
        'Currency', on_delete=models.SET_NULL, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    class Meta:
        verbose_name_plural = "user"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Currency(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "currency"

    def __str__(self):
        return self.currency
    

class CustomUserManager(BaseUserManager):
    def create_user(self, email, firstname=None, lastname=None, password=None):
        """Create and return a regular user with email and password."""
        if not email:
            raise ValueError("Users must have an email address")
        
        firstname = firstname or "Google"  # Default if missing
        lastname = lastname or "User"  # Default if missing
        
        user = self.model(email=self.normalize_email(email),
                          firstname=firstname, lastname=lastname)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # This allows Google users to log in without a password

        user.is_active = True
        user.save(using=self._db)
        return user
