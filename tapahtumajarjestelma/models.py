from django.db import models
from django.contrib.auth.models import User
import datetime
import uuid


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organizer = models.BooleanField(default=False)


class Tapahtuma(models.Model):
    tapahtuma_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nimi = models.CharField(max_length=60)
    paikka_maara = models.IntegerField(default=1)
    kotisivu = models.CharField(max_length=60, default="")

    @staticmethod
    def get(tapahtuma_id):
        return Tapahtuma.objects.filter(tapahtuma_id=tapahtuma_id).first()

    @staticmethod
    def on_tilaa(tapahtuma_id):
        tapahtuma = Tapahtuma.get(tapahtuma_id)
        varatut_paikat = Varaus.get_ilmoittautujat(tapahtuma_id)
        return (varatut_paikat == None and tapahtuma.paikka_maara > 0) or (len(varatut_paikat) < tapahtuma.paikka_maara)


class Varaus(models.Model):
    varaus_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tapahtuma_id = models.ForeignKey(Tapahtuma, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.datetime.today)

    @staticmethod
    def tapahtuma(tapahtuma_id):
        return Tapahtuma.objects.filter(tapahtuma_id=tapahtuma_id).first()

    @staticmethod
    def get_ilmoittautujat(tapahtuma_id):
        return Varaus.objects.filter(tapahtuma_id=tapahtuma_id)

    @staticmethod
    def get_varatut(user):
        return Varaus.objects.filter(user=user)

    @staticmethod
    def varattu(user_id, tapahtuma_id):
        return Varaus.objects.filter(
            user_id=user_id, tapahtuma_id=tapahtuma_id).exists()

    @staticmethod
    def peru(user_id, tapahtuma_id):
        return Varaus.objects.filter(user=user_id, tapahtuma_id=tapahtuma_id).delete()
