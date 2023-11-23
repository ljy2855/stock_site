from django.db import models
from django.contrib.auth.models import User
from page.models import *
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save


    
class HoldingStock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock,on_delete=models.CASCADE)
    cnt = models.IntegerField(default=0)

    def get_value(self):
        return self.cnt * self.stock.current_price
class UserProfile(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.IntegerField(default = 1000000)
    total_balance = models.IntegerField(default=0)
    def __str__(self): 
        return self.user.username
    def update_total_balance(self):
        holdings = HoldingStock.objects.filter(user=self.user)
        self.total_balance = self.money
        for holding in holdings:
            self.total_balance += holding.stock.current_price * holding.cnt
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.user_profile.save()
# Create your models here.
