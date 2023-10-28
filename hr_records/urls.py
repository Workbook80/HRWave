from django.urls import path
from . import views

app_name = 'hr_records'
urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('employee_list/', views.employee_list, name='employee_list'),
    path('vacation_list/', views.vacation_list, name='vacation_list'),
    path('business_trip_list/', views.business_trip_list, name='business_trip_list'),
    path('sick_leave_list/', views.sick_leave_list, name='sick_leave_list'),
    path('employee_list/<int:employee_id>/', views.employee_detail, name='employee_detail'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('create_vacation/', views.create_vacation, name='create_vacation'),
    path('create_business_trip/', views.create_business_trip, name='create_business_trip'),
    path('create_sick_leave/', views.create_sick_leave, name='create_sick_leave'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('export_json/', views.export_json, name='export_json'),
    path('export_pdf/<int:employee_id>/', views.export_pdf, name='export_pdf'),
    path('vacation_pdf', views.vacation_pdf, name='vacation_pdf'),
    path('business_trip_pdf', views.business_trip_pdf, name='business_trip_pdf'),
    path('sick_leave_pdf', views.sick_leave_pdf, name='sick_leave_pdf'),
]

