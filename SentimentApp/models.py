from django.db import models

# Create your models here.
class mailDataBase(models.Model):
    Name = models.CharField(max_length=50)
    Email = models.EmailField(max_length=254)
    Brand = models.CharField(max_length=50)