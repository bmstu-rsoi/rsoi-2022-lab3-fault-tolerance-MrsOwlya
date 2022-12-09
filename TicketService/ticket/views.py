from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Ticket
from .serializers import TicketSerializer
from circuitbreaker import circuit

FAIL = 5
TIMEOUT = 10


# Create your views here.
@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def user_tickets(request):
    user = request.headers['X-User-Name']
    try:
        tickets = Ticket.objects.filter(username=user)
        if tickets is not None:
            serializer = TicketSerializer(tickets, many=True)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse({'message': 'No tickets'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def one_ticket_info(request, ticketId):
    user = request.headers['X-User-Name']
    try:
        ticket = Ticket.objects.filter(username=user, ticket_uid=ticketId).first()
        if ticket is not None:
            serializer = TicketSerializer(ticket, many=False)
            return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse({'message': 'No ticket'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['POST'])
def buy_ticket(request):
    user = request.headers['X-User-Name']
    try:
        data = {
            "username": user,
            "flight_number": request.data["flightNumber"],
            "price": request.data["price"],
            "status": Ticket.StatusType.P
        }
        serializer = TicketSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        s = serializer.save()
        data = {
            "ticketUid": s.ticket_uid,
            "flightNumber": s.flight_number,
            "price": s.price,
            "status": s.status
        }
        return JsonResponse(data, status=status.HTTP_201_CREATED, safe=False)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['PATCH'])
def cancel_ticket(request, ticketId):
    user = request.headers['X-User-Name']
    try:
        ticket = Ticket.objects.get(ticket_uid=ticketId, username=user)
        if ticket.status != 'CANCELED':
            ticket.status = 'CANCELED'
            ticket.save()
            return JsonResponse({'message': 'Ticket is successfully canceled'}, status=status.HTTP_204_NO_CONTENT)
        return JsonResponse({'message': 'Ticket is already canceled'}, status=status.HTTP_208_ALREADY_REPORTED)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def manage(request):
    return JsonResponse({}, status=status.HTTP_200_OK, safe=False)