import datetime

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Privilege, PrivilegeHistory
from .serializers import PrivilegeSerializer, PrivilegeHistorySerializer
from circuitbreaker import circuit, CircuitBreakerMonitor

FAIL = 5
TIMEOUT = 10


# Create your views here.
def add_to_history(privilege, ticket, balance_diff, op):
    try:
        history = {
            "privilege_id": privilege,
            "ticket_uid": ticket,
            "datetime": datetime.datetime.now(),
            "balance_diff": balance_diff,
            "operation_type": op
        }
        serializer = PrivilegeHistorySerializer(data=history)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({}, status=status.HTTP_201_CREATED, safe=False)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def show_user_info(request):
    user = request.headers['X-User-Name']
    try:
        info = Privilege.objects.filter(username=user).first()
        if info is not None:
            serializer = PrivilegeSerializer(info, many=False)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse({'message': 'No user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def show_user_info_and_history(request):
    user = request.headers['X-User-Name']
    try:
        info = Privilege.objects.filter(username=user).first()
        if info is not None:
            history = info.privilegehistory_set.all()
            hs = []
            for h in history:
                hs.append({
                    "date": h.datetime,
                    "ticketUid": h.ticket_uid,
                    "balanceDiff": h.balance_diff,
                    "operationType": h.operation_type
                })

            data = {
                "balance": info.balance,
                "status": info.status,
                "history": hs
            }
            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse({'message': 'No user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['PATCH'])
def count_bonuses(request):
    global balance_diff, op, payByBonuses, payByMoney
    user = request.headers['X-User-Name']
    try:
        user_bonus = Privilege.objects.get(username=user)
        price = int(request.data["price"])
        if request.data["paidFromBalance"] == 'true':
            if price < user_bonus.balance:
                payByBonuses = price
                payByMoney = 0
                balance_diff = price
                user_bonus.balance = user_bonus.balance - price
                user_bonus.save()
            else:
                payByBonuses = user_bonus.balance
                payByMoney = price - user_bonus.balance
                balance_diff = user_bonus.balance
                user_bonus.balance = 0
                user_bonus.save()
            op = PrivilegeHistory.OperationType.DEBIT
        else:
            payByBonuses = 0
            payByMoney = price
            balance_diff = price / 10
            user_bonus.balance += balance_diff
            user_bonus.save()
            op = PrivilegeHistory.OperationType.FILL

        data = {
            "paidByBonuses": payByBonuses,
            "paidByMoney": payByMoney,
            "privilege": {
                "balance": user_bonus.balance,
                "status": user_bonus.status
            }
        }
        add_to_history(user_bonus.id, request.data["ticketUid"], balance_diff, op)
        return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
    except Exception as e:
        return JsonResponse({'user': user, 'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['PATCH'])
def count_bonuses_from_return(request, ticket):
    user = request.headers['X-User-Name']
    try:
        user_bonus = Privilege.objects.get(username=user)
        history = PrivilegeHistory.objects.filter(privilege_id=user_bonus.id, ticket_uid=ticket).order_by('-datetime')[
            0]
        print(history.operation_type)
        print(user_bonus.balance)
        if history.operation_type == PrivilegeHistory.OperationType.FILL:
            user_bonus.balance -= history.balance_diff
            op = PrivilegeHistory.OperationType.DEBIT
            if user_bonus.balance < 0:
                user_bonus.balance = 0
            user_bonus.save()
        if history.operation_type == PrivilegeHistory.OperationType.DEBIT:
            op = PrivilegeHistory.OperationType.FILL
            user_bonus.balance += history.balance_diff
            user_bonus.save()
        print(op)
        print(user_bonus.balance)
        add_to_history(user_bonus.id, ticket, history.balance_diff, op)
        return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def manage(request):
    return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
