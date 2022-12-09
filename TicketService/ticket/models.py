import uuid

from django.db import models


# Create your models here.
class Ticket(models.Model):
    class StatusType(models.TextChoices):
        P = 'PAID', 'Paid'
        C = 'CANCELED', 'Canceled'

    id = models.AutoField('ID', primary_key=True)
    ticket_uid = models.UUIDField('ID билета', default=uuid.uuid4, unique=True)
    username = models.CharField('Пользователь', max_length=80, null=False)
    flight_number = models.CharField('Номер рейса', max_length=20, null=False)
    price = models.IntegerField('Стоимость', null=False)
    status = models.CharField('Статус', max_length=20, null=False, choices=StatusType.choices)
