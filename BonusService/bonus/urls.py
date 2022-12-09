from django.urls import path
from . import views

urlpatterns = [
    path('user_info', views.show_user_info),
    path('balance_and_history', views.show_user_info_and_history),
    path('count_bonuses', views.count_bonuses),
    path('count_bonuses_from_return/<uuid:ticket>', views.count_bonuses_from_return),
    path('manage/health', views.manage)
]
