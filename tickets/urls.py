from django.urls import path
from . import views

urlpatterns = [
    path('purchase/<int:event_id>/', views.purchase_ticket_view, name='purchase_ticket'),
    path('validate/', views.validate_ticket_view, name='validate_ticket'),
    path('report/<int:event_id>/<str:format_type>/', views.download_report_view, name='download_report'),
]
