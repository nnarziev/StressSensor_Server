from django.db import models
from django.db.models.deletion import CASCADE
import datetime


# Create your models here.
class Response(models.Model):
    username = models.ForeignKey('user.Participant', on_delete=CASCADE, default="")
    day_num = models.SmallIntegerField(default=None)
    ema_order = models.SmallIntegerField(default=None)
    answer1 = models.SmallIntegerField(default=-1)
    answer2 = models.SmallIntegerField(default=-1)
    answer3 = models.SmallIntegerField(default=-1)
    answer4 = models.SmallIntegerField(default=-1)
    time_expected = models.BigIntegerField(default=0)
    time_responded = models.BigIntegerField(default=0)
    lof_value = models.FloatField(default=-1)


    def expected_date(self):
        return datetime.datetime.fromtimestamp(self.time_expected).date()
