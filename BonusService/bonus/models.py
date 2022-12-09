from django.db import models
import uuid


# Create your models here.
class Privilege(models.Model):

    class StatusType(models.TextChoices):
        B = 'BRONZE', 'Bronze'
        S = 'SILVER', 'Silver'
        G = 'GOLD', 'Gold'

    id = models.AutoField('ID', primary_key=True)
    username = models.CharField('Пользователь', max_length=80, unique=True, null=False)
    status = models.CharField('Статус', max_length=80, choices=StatusType.choices, default=StatusType.B, null=True)
    balance = models.IntegerField('Баланс')


class PrivilegeHistory(models.Model):

    class OperationType(models.TextChoices):
        FILL = 'FILL_IN_BALANCE', 'Fill in balance'
        DEBIT = 'DEBIT_THE_ACCOUNT', 'Debit the account'

    id = models.AutoField('ID', primary_key=True)
    privilege_id = models.ForeignKey(Privilege, on_delete=models.CASCADE)
    ticket_uid = models.UUIDField('ID билета', default=uuid.uuid4, null=False)
    datetime = models.DateTimeField('Дата и время', null=False)
    balance_diff = models.IntegerField('Разница баланса', null=False)
    operation_type = models.CharField('Тип операции', max_length=20, choices=OperationType.choices, null=False)
