import os

from django.conf import settings
import requests
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from circuitbreaker import circuit
from .tasks import testing, turn_ticket, buy_ticket, turn_bonus, buy_bonus
import redis

FAIL = 3
TIMEOUT = 5

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


# Create your views here.
def check_user(request):
    user = request.headers.get('X-User-Name')
    if user is not None:
        return user
    else:
        return False


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def flights_list(request):
    flights = requests.get(
        'http://' + os.environ.get('FLIGHT', 'localhost') + ':8060/api/v1/flights?page={}&size={}'.format(
            request.GET.get('page')
            , request.GET.get('size')))
    if flights.status_code != 200:
        return JsonResponse(flights.json(), status=status.HTTP_400_BAD_REQUEST, safe=False)
    testing.delay(request.method)
    return JsonResponse(flights.json(), status=status.HTTP_200_OK, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def user_info(request):
    user = check_user(request)
    if user:
        tickets = requests.get('http://' + os.environ.get('TICKET', 'localhost') + ':8070/api/v1/user_tickets'
                               , headers={'X-User-Name': f'{user}'})
        if tickets.status_code == 200:
            tickets = tickets.json()
            ts = []
            for t in tickets:
                fl = requests.get('http://' + os.environ.get('FLIGHT', 'localhost') + ':8060/api/v1/flights/{}'.format(
                    t['flight_number']))
                if fl.status_code == 200:
                    fl = fl.json()
                    data = {
                        "ticketUid": t['ticket_uid'],
                        "flightNumber": t['flight_number'],
                        "fromAirport": fl['fromAirport'],
                        "toAirport": fl['toAirport'],
                        "date": fl['date'],
                        "price": fl['price'],
                        "status": t['status']
                    }
                    ts.append(data)
            try:
                info = requests.get("http://" + os.environ.get('BONUS', 'localhost') + ":8050/api/v1/user_info"
                                    , headers={'X-User-Name': f'{user}'})
                if info.status_code == 200:
                    info = info.json()
                    data = {
                        "tickets": ts,
                        "privilege": {
                            "balance": info['balance'],
                            "status": info['status']
                        }
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
                return JsonResponse(info.json(), status=info.status_code)
            except requests.exceptions.ConnectionError:
                data = {
                        "tickets": ts,
                        "privilege": {
                        }
                    }
                return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse(tickets.json(), status=tickets.status_code)
    return JsonResponse({'message': 'user is necessary'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def privilege_info(request):
    user = check_user(request)
    print(user)
    if user:
        try:
            info = requests.get("http://" + os.environ.get('BONUS', 'localhost') + ":8050/api/v1/balance_and_history"
                                , headers={'X-User-Name': f'{user}'})
            if info.status_code == 200:
                return JsonResponse(info.json(), status=status.HTTP_200_OK, safe=False)
            return JsonResponse(info.json(), status=info.status_code, safe=False)
        except requests.exceptions.ConnectionError:
            return JsonResponse({'message':'Bonus Service unavailable'},status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return JsonResponse({'message': 'user is necessary'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET', 'POST'])
def user_tickets_or_buy(request):
    user = check_user(request)
    if user:
        if request.method == 'GET':
            user_tickets = requests.get("http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/user_tickets"
                                        , headers={'X-User-Name': f'{user}'})
            if user_tickets.status_code == 200:
                user_tickets = user_tickets.json()
                ts = []
                for t in user_tickets:
                    fl = requests.get(
                        "http://" + os.environ.get('FLIGHT', 'localhost') + ":8060/api/v1/flights/{}".format(
                            t['flight_number']))
                    if fl.status_code == 200:
                        fl = fl.json()
                        data = {
                            "ticketUid": t['ticket_uid'],
                            "flightNumber": t['flight_number'],
                            "fromAirport": fl['fromAirport'],
                            "toAirport": fl['toAirport'],
                            "date": fl['date'],
                            "price": fl['price'],
                            "status": t['status']
                        }
                        ts.append(data)
                return JsonResponse(ts, status=status.HTTP_200_OK, safe=False)
            return JsonResponse(user_tickets.json(), status=user_tickets.status_code, safe=False)
        if request.method == 'POST':
            flight = requests.get("http://" + os.environ.get('FLIGHT', 'localhost') + ":8060/api/v1/flights/{}".format(
                request.data["flightNumber"]))
            if flight.status_code == 200 and int(flight.json()['price']) == int(request.data["price"]) and \
                    (not bool(request.data["paidFromBalance"]) or bool(request.data["paidFromBalance"])):
                ticket = requests.post(
                    "http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/buy_ticket",
                    data=request.data,
                    headers={'X-User-Name': f'{user}'})
                if ticket.status_code != 201:
                    return JsonResponse(ticket.json(), status=ticket.status_code, safe=False)
                try:
                    count_bonus = requests.patch(
                        "http://" + os.environ.get('BONUS', 'localhost') + ":8050/api/v1/count_bonuses"
                        , data={
                            "paidFromBalance": request.data["paidFromBalance"],
                            "price": request.data["price"],
                            "ticketUid": ticket.json()["ticketUid"]
                        }
                        , headers={'X-User-Name': f'{user}'})
                    print("ФФФФФФФФФФФФФФФФФФФФФФФФФФФФ")
                    if count_bonus.status_code != 200:
                        return JsonResponse(count_bonus.json(), status=count_bonus.status_code, safe=False)
                    data = {}
                    data.update(flight.json())
                    data.update(ticket.json())
                    data.update(count_bonus.json())
                    return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
                except requests.exceptions.ConnectionError:
                    print("ЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫЫ")
                    resp = requests.patch(
                        "http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/cancel_ticket/{}".format(ticket.json()["ticketUid"])
                        , headers={'X-User-Name': f'{user}'})
                    return JsonResponse({'message': 'Bonus Service unavailable'},
                                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return JsonResponse({'message': 'user is necessary'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET', 'DELETE'])
def user_ticket_info_or_cancel(request, ticketId):
    user = check_user(request)
    print('ti:'+str(ticketId))
    if user:
        if request.method == 'GET':
            user_ticket = requests.get(
                "http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/one_ticket_info/{}".format(ticketId)
                , headers={'X-User-Name': f'{user}'})
            if user_ticket.status_code == 200:
                user_ticket = user_ticket.json()
                fl = requests.get("http://" + os.environ.get('FLIGHT', 'localhost') + ":8060/api/v1/flights/{}".format(
                    user_ticket['flight_number']))
                if fl.status_code == 200:
                    fl = fl.json()
                    data = {
                        "ticketUid": user_ticket['ticket_uid'],
                        "flightNumber": user_ticket['flight_number'],
                        "fromAirport": fl['fromAirport'],
                        "toAirport": fl['toAirport'],
                        "date": fl['date'],
                        "price": fl['price'],
                        "status": user_ticket['status']
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
            return JsonResponse({'message': 'no ticket'}, status=status.HTTP_404_NOT_FOUND, safe=False)
        if request.method == 'DELETE':
            ticket = requests.get(
                "http://" + os.environ.get('TICKET', 'localhost') + ":8070/api/v1/one_ticket_info/{}".format(ticketId)
                , headers={'X-User-Name': f'{user}'})
            if ticket.status_code == 200:
                t = turn_ticket.delay(user, ticketId).task_id
                return JsonResponse({'message': 'Ticket successfully cancelled'}, status=status.HTTP_204_NO_CONTENT
                                    , safe=False)
        print('xyz')
    return JsonResponse({'message': 'user is necessary'}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def manage(request):
    return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
