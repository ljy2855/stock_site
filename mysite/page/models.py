from django.db import models

class Stock(models.Model):
    
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=7)
    current_price = models.IntegerField(default=0)
    prev_price = models.IntegerField(default=0)
    high_price = models.IntegerField(default=0)
    low_price = models.IntegerField(default=0)
    opening_price = models.IntegerField(default=0)
    up_down = models.FloatField(default=0)
    volume = models.IntegerField(default=0)
    updated_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.name
    



# Create your models here.
