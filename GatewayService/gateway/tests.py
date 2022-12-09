import json
import os

from django.test.client import Client

from django.test import TestCase

# Create your tests here.

save_ticket = None


class Lab2TestCase(TestCase):

    def setUp(self):
        pass

    def test_show_flights(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        page = 1
        size = 5
        result = c.get(
            "http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/flights?page={}&size={}".format(page,
                                                                                                               size))
        print("api/v1/flights?page={}&size={}")
        print(result.json())
        self.assertEqual(result.status_code, 200)

    def test_show_my_tickets(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/tickets")
        self.assertEqual(result.status_code, 200)

    def test_show_my_one_ticket(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        tickets = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/tickets")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/tickets/{}"
                       .format(tickets.json()[0]['ticketUid']))
        self.assertEqual(result.status_code, 200)

    def test_show_me(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/me")
        print("/api/v1/me")
        print(result.json())
        self.assertEqual(result.status_code, 200)

    def test_show_me_no_user(self):
        c = Client(HTTP_X_USER_NAME="no_owlya")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/me")
        self.assertEqual(result.status_code, 404)

    def test_my_balance(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/privilege")
        print("/api/v1/privilege")
        print(result.json())
        self.assertEqual(result.status_code, 200)

    def test_my_balance_no_user(self):
        c = Client(HTTP_X_USER_NAME="no_owlya")
        result = c.get("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/privilege")
        self.assertEqual(result.status_code, 404)

    def test_buy_ticket(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        data = {
            "flightNumber": "AFL031",
            "price": 1500,
            "paidFromBalance": True
        }
        result = c.post("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/tickets", data=data)
        print("/api/v1/tickets")
        print(result.json())
        self.assertEqual(result.status_code, 200)

    def test_buy_ticket_no_flight(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        data = {
            "flightNumber": "AFL032",
            "price": 1500,
            "paidFromBalance": True
        }
        result = c.post("http://" + os.environ.get('GATEWAY', 'localhost') + ":8080/api/v1/tickets", data=data)
        self.assertEqual(result.status_code, 404)

    def test_cancel_ticket(self):
        c = Client(HTTP_X_USER_NAME="owlya")
        pass
