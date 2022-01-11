from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from annoying.fields import AutoOneToOneField

class Stock(models.Model):
    class Meta :
        abstract = True
    name = models.CharField(max_length=20)
    price = models.IntegerField(default = 0)
    time = models.DateTimeField(default= timezone.now)


    def __str__(self):
        return self.name

class StockData(Stock):
    pre_price = models.IntegerField(default=0)
    high_price = models.IntegerField(default=0)
    low_price = models.IntegerField(default=0)

    def __str__(self):
        return self.name + "_" + self.time.strftime("%Y/%m/%d/%H:%M")

    def up_down(self):
        per = round(float((self.price - self.pre_price) / self.pre_price) * 100,2)
        return per

class StockHistory(Stock):
    def __str__(self):
        return self.name + "_" + self.time.strftime("%Y/%m/%d/%H:%M")




class User_Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    money = models.IntegerField(default = 1000000)
    def __str__(self): 
        return self.user.username

class HoldingStock(Stock):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cnt = models.IntegerField(default = 0)
    total_price = models.IntegerField(default = 0)


    def __str__(self):
        return self.name + "_" + self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        User_Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.user_profile.save()




