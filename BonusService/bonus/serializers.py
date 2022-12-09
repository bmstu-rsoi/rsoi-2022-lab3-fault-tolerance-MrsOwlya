from rest_framework import serializers
from .models import Privilege, PrivilegeHistory


class PrivilegeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta:
        model = Privilege
        fields = \
            [
                'id'
                , 'username'
                , 'status'
                , 'balance'
            ]


class PrivilegeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivilegeHistory
        fields = \
            [
                'id'
                , 'privilege_id'
                , 'ticket_uid'
                , 'datetime'
                , 'balance_diff'
                , 'operation_type'
            ]
