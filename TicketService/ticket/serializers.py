from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = \
            ['id'
                , 'ticket_uid'
                , 'username'
                , 'flight_number'
                , 'price'
                , 'status'
             ]
