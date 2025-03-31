from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    email = models.EmailField(unique=True)
    subscription = models.CharField(max_length=100,default="Free")
    sub_date = models.DateField()
    exp_date = models.DateField()
    auto_renewal = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["password","subscription","sub_date","exp_date"]

class Content(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=1500)
    category = models.CharField(max_length=200)
    tags = models.CharField(max_length=1000)
    ai_score = models.IntegerField()

class UserInteraction(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    content = models.ForeignKey(Content,on_delete=models.CASCADE)
    interaction = models.CharField(max_length=10)
