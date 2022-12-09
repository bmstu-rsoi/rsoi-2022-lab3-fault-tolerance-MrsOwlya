from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import AirportSerializer, FlightSerializer
from .models import Airport, Flight
from circuitbreaker import circuit
from django.shortcuts import get_object_or_404

FAIL = 5
TIMEOUT = 10


# Create your views here.
@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def flights_page(request):
    try:
        page = int(request.GET.get('page'))
        size = int(request.GET.get('size'))
        if page is not None and size is not None:
            page_start = size * (page - 1)
            page_end = size * page - 1
            fl_page = Flight.objects.all()[page_start:page_end]
        else:
            fl_page = Flight.objects.all()
        fs = []
        for f in fl_page:
            af = " ".join([f.from_airport_id.city, f.from_airport_id.name])
            at = " ".join([f.to_airport_id.city, f.to_airport_id.name])
            fs.append({
                "flightNumber": f.flight_number,
                "fromAirport": af,
                "toAirport": at,
                "date": f.datetime,
                "price": f.price
            })
        data = {
            "page": page,
            "pageSize": size,
            "totalElements": fl_page.count(),
            "items": fs
        }
        return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def flight_info(request, flightNum):
    try:
        flight = Flight.objects.filter(flight_number=flightNum).first()
        if flight is not None:
            af = " ".join([flight.from_airport_id.city, flight.from_airport_id.name])
            at = " ".join([flight.to_airport_id.city, flight.to_airport_id.name])
            data = {
                "flightNumber": flight.flight_number,
                "fromAirport": af,
                "toAirport": at,
                "date": flight.datetime,
                "price": flight.price
            }
            return JsonResponse(data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse({'message': 'No flight'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({'message': '{}'.format(e)}, status=status.HTTP_400_BAD_REQUEST, safe=False)


@circuit(failure_threshold=FAIL, recovery_timeout=TIMEOUT)
@api_view(['GET'])
def manage(request):
    return JsonResponse({}, status=status.HTTP_200_OK, safe=False)
