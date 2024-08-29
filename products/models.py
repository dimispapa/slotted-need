from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=7,
                                     decimal_places=2,
                                     validators=[MinValueValidator(0.00)])
