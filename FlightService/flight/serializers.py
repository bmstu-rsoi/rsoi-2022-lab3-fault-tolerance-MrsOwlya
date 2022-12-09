from rest_framework import serializers
from .models import Airport, Flight


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = \
            [
                'id'
                , 'name'
                , 'city'
                , 'country'
            ]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = \
            [
                'flight_number'
                , 'datetime'
                , 'from_airport_id'
                , 'to_airport_id'
                , 'price'
            ]
