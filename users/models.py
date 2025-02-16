from django.db import models

# Create your models here.
# users/models.py
class Currency(models.Model):
    # Define a currency model with name, and symbol as an example
    id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = "currency"

    def __str__(self):
        return self.currency

class User(models.Model):
    # ID is auto-generated, so no need to define it explicitly
    id = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=128)
    lastname = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed password later
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "user"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
