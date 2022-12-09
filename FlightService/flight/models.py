from django.db import models


# Create your models here.
class Airport(models.Model):
    name = models.CharField('Наименование', max_length=255)
    city = models.CharField('Город', max_length=255)
    country = models.CharField('Страна', max_length=255)

    def __str__(self):
        return self.name


class Flight(models.Model):
    flight_number = models.CharField('Номер рейса', unique=True, max_length=20, null=False)
    datetime = models.DateTimeField('Дата и время', null=False)
    from_airport_id = models.ForeignKey(Airport, related_name='from_airport_id', on_delete=models.CASCADE)
    to_airport_id = models.ForeignKey(Airport, related_name='to_airport_id', on_delete=models.CASCADE)
    price = models.IntegerField('Стоимость', null=False)

    def __str__(self):
        return self.flight_number


