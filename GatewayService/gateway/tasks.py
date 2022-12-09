import os

from GatewayService.celery import celery_app as app
import requests
from celery import shared_task
import logging
from django.http import JsonResponse
from rest_framework import status
from celery.result import AsyncResult


@app.task
def testing(method):
    print(method + ' I WORK!!!!!!!!!!!!!!!!!!!!')


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 15})
def turn_ticket(self, user, ticketId):
    logging.info(ticketId + '!!!!!!!!!!!!!!!')
    resp = requests.patch(
            "http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/cancel_ticket/{}".format(ticketId)
            , headers={'X-User-Name': f'{user}'})
    if resp.status_code == 204:
        requests.patch(
            'http://' + os.environ.get('BONUS', 'localhost') + ':8050/api/v1/count_bonuses_from_return/{}'.format(
                ticketId)
            , headers={'X-User-Name': f'{user}'})
    return True


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 5})
def turn_bonus(self, user, ticketId):
    return requests.patch(
        'http://' + os.environ.get('BONUS', 'localhost') + ':8050/api/v1/count_bonuses_from_return/{}'.format(
            ticketId)
        , headers={'X-User-Name': f'{user}'}).json()



@app.task(bind=True, max_retries=10)
def buy_ticket(self, data, user):
    try:
        print('BLYAT')
        ticket = requests.post('http://' + os.environ.get('TICKET', 'localhost') + ':8070/api/v1/buy_ticket',
                               data=data,
                               headers={'X-User-Name': f'{user}'})
        print(ticket.json())
    except Exception as e:
        raise self.retry(exc=e, countdown=3)


@app.task(bind=True, max_retries=10)
def buy_bonus(self, data, user, ticket):
    try:
        count_bonus = requests.patch('http://' + os.environ.get('BONUS', 'localhost') + ':8050/api/v1/count_bonuses'
                                     , data={
                "paidFromBalance": data["paidFromBalance"],
                "price": data["price"],
                "ticketUid": ticket
            }
                                     , headers={'X-User-Name': f'{user}'})
        if count_bonus.status_code != 200:
            turn_ticket.delay(user, ticket)
        print(count_bonus.json())
    except Exception as e:
        raise self.retry(exc=e, countdown=3)
