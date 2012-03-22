from django.db import models

# Create your models here.
class Checklist(models.Model):
    Name=models.CharField(max_length=200)
    
class Item(models.Model):
    Name=models.CharField(max_length=200)
    Checklist=models.ForeignKey(Checklist, related_name="items")
    Data=models.CharField(max_length=800)
    
    
    TYPE_CHOICES = (
        ('0', 'Male'),
        ('F', 'Female'),
    )
