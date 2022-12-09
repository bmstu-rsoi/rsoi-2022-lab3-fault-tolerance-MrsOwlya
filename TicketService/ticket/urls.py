from django.urls import path
from . import views

urlpatterns = [
    path('user_tickets', views.user_tickets),
    path('buy_ticket', views.buy_ticket),
    path('one_ticket_info/<uuid:ticketId>', views.one_ticket_info),
    path('cancel_ticket/<uuid:ticketId>', views.cancel_ticket),
    path('manage/health', views.manage)
]