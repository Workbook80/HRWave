from django.contrib import admin
from .models import Employee, Vacation, BusinessTrip, SickLeave


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'position', 'hire_date')
    list_filter = ('hire_date', 'position')


@admin.register(Vacation)
class VacationAdmin(admin.ModelAdmin):
    list_display = ('employee_vacation', 'start_date_vacation', 'end_date_vacation')
    list_filter = ('start_date_vacation', 'end_date_vacation')


@admin.register(BusinessTrip)
class BusinessTripAdmin(admin.ModelAdmin):
    list_display = ('employee_business_trip', 'start_date_business_trip', 'end_date_business_trip')
    list_filter = ('start_date_business_trip', 'end_date_business_trip')


@admin.register(SickLeave)
class SickLeaveAdmin(admin.ModelAdmin):
    list_display = ('employee_sick_leave', 'start_date_sick_leave', 'end_date_sick_leave')
    list_filter = ('start_date_sick_leave', 'end_date_sick_leave')

