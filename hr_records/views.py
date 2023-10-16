from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Vacation, BusinessTrip, SickLeave
from .forms import EmployeeForm, VacationForm, BusinessTripForm, SickLeaveForm
from django.core.paginator import Paginator
from django.db.models import Q

# JSON
from django.http import JsonResponse, Http404
from urllib.parse import quote

# PDF
from django.http import FileResponse
from reportlab.lib.pagesizes import letter, portrait
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('hr_records:employee_list')
        else:
            messages.error(request, 'Доступ запрещен. Проверьте учетные данные.')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'hr_records/login.html', context)


@login_required(login_url='hr_records:login')
def logout_view(request):
    logout(request)
    return redirect('hr_records:login')


@login_required(login_url='hr_records:login')
def search_and_paginate(request, model, search_field, date_field_start, date_field_end, items_per_page):
    search_query = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    queryset = model.objects.all().order_by(search_field)

    if search_query:
        search_query = search_query.capitalize()
        filter_kwargs = {f'{search_field}__icontains': search_query}
        queryset = queryset.filter(**filter_kwargs)

    if year:
        filter_condition = Q(**{f'{date_field_start}__year': year}) | Q(**{f'{date_field_end}__year': year})
        queryset = queryset.filter(filter_condition)

    if month:
        filter_condition = (Q(**{f'{date_field_start}__month': month}) | Q(**{f'{date_field_end}__month': month}))
        queryset = queryset.filter(filter_condition)

    if model != Employee:
        queryset = queryset.order_by('-' + date_field_start)

    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    items = paginator.get_page(page_number)
    return items, search_query


@login_required(login_url='hr_records:login')
def employee_list(request):
    employees, search_query = search_and_paginate(request, Employee, 'last_name', None, None, 10)
    context = {'employees': employees, 'search_query': search_query, 'items': employees}
    return render(request, 'hr_records/employee_list.html', context)


@login_required(login_url='hr_records:login')
def vacation_list(request):
    vacations, search_query = search_and_paginate(request, Vacation, 'employee_vacation__last_name',
                                                  'start_date_vacation', 'end_date_vacation', 3)
    context = {'vacations': vacations, 'search_query': search_query, 'items': vacations}
    return render(request, 'hr_records/vacation_list.html', context)


@login_required(login_url='hr_records:login')
def business_trip_list(request):
    business_trips, search_query = search_and_paginate(request, BusinessTrip, 'employee_business_trip__last_name',
                                                       'start_date_business_trip', 'end_date_business_trip', 3)
    context = {'business_trips': business_trips, 'search_query': search_query, 'items': business_trips}
    return render(request, 'hr_records/business_trip_list.html', context)


@login_required(login_url='hr_records:login')
def sick_leave_list(request):
    sick_leaves, search_query = search_and_paginate(request, SickLeave, 'employee_sick_leave__last_name',
                                                    'start_date_sick_leave', 'end_date_sick_leave', 3)
    context = {'sick_leaves': sick_leaves, 'search_query': search_query, 'items': sick_leaves}
    return render(request, 'hr_records/sick_leave_list.html', context)


@login_required(login_url='hr_records:login')
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    vacations = Vacation.objects.filter(employee_vacation=employee)
    vacations = vacations.order_by('-start_date_vacation')
    paginator = Paginator(vacations, 4)
    page_number = request.GET.get('vacations_page')
    vacations_page = paginator.get_page(page_number)

    business_trips = BusinessTrip.objects.filter(employee_business_trip=employee)
    business_trips = business_trips.order_by('-start_date_business_trip')
    business_trips_paginator = Paginator(business_trips, 4)
    business_trips_page_number = request.GET.get('business_trips_page')
    business_trips_page = business_trips_paginator.get_page(business_trips_page_number)

    sick_leaves = SickLeave.objects.filter(employee_sick_leave=employee)
    sick_leaves = sick_leaves.order_by('-start_date_sick_leave')
    sick_leaves_paginator = Paginator(sick_leaves, 4)
    sick_leaves_page_number = request.GET.get('sick_leaves_page')
    sick_leaves_page = sick_leaves_paginator.get_page(sick_leaves_page_number)

    context = {
        'employee': employee,
        'vacations_page': vacations_page,
        'business_trips_page': business_trips_page,
        'sick_leaves_page': sick_leaves_page
    }

    return render(request, 'hr_records/employee_detail.html', context)


@login_required(login_url='hr_records:login')
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hr_records:employee_list')
    else:
        form = EmployeeForm()

    context = {'form': form}
    return render(request, 'hr_records/create_employee.html', context)


@login_required(login_url='hr_records:login')
def create_record(request, record_type):
    employee_id = request.GET.get('employee_id')
    employee = Employee.objects.get(pk=employee_id)
    form = None

    if request.method == 'POST':
        if record_type == 'vacation':
            form = VacationForm(request.POST)
        elif record_type == 'business_trip':
            form = BusinessTripForm(request.POST)
        elif record_type == 'sick_leave':
            form = SickLeaveForm(request.POST)

        if form.is_valid():
            record = form.save(commit=False)
            setattr(record, f'employee_{record_type}_id', employee_id)
            record.save()
            return redirect('hr_records:employee_list')
    else:
        if record_type == 'vacation':
            form = VacationForm()
        elif record_type == 'business_trip':
            form = BusinessTripForm()
        elif record_type == 'sick_leave':
            form = SickLeaveForm()

    context = {'form': form, 'employee': employee}
    return render(request, f'hr_records/create_{record_type}.html', context)


@login_required(login_url='hr_records:login')
def create_vacation(request):
    return create_record(request, 'vacation')


@login_required(login_url='hr_records:login')
def create_business_trip(request):
    return create_record(request, 'business_trip')


@login_required(login_url='hr_records:login')
def create_sick_leave(request):
    return create_record(request, 'sick_leave')


@login_required(login_url='hr_records:login')
def edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('hr_records:employee_detail', employee_id=employee.employee_id)
    else:
        form = EmployeeForm(instance=employee)

    context = {'form': form, 'employee': employee}
    return render(request, 'hr_records/edit_employee.html', context)


@login_required(login_url='hr_records:login')
def export_json(request):
    employee_id = request.GET.get('employee_id')

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        raise Http404('Сотрудник не найден')

    employee_data = {
        'employee_id': employee.employee_id,
        'last_name': employee.last_name,
        'first_name': employee.first_name,
        'middle_name': employee.middle_name,
        'position': employee.position,
        'hire_date': employee.hire_date.strftime('%d/%m/%Y'),
        'email': employee.email,
        'phone_number': employee.phone_number,
        # Добавьте другие поля сотрудника, которые вам нужны
        'vacations': [{'type_vacation': vacation.type_vacation,
                       'start_date': vacation.start_date_vacation.strftime('%d/%m/%Y'),
                       'end_date': vacation.end_date_vacation.strftime('%d/%m/%Y')}
                      for vacation in employee.vacation_set.all()],
        'business_trips': [{'destination': business_trip.destination,
                            'start_date': business_trip.start_date_business_trip.strftime('%d/%m/%Y'),
                            'end_date': business_trip.end_date_business_trip.strftime('%d/%m/%Y')}
                           for business_trip in employee.businesstrip_set.all()],
        'sick_leaves': [{'reason': sick_leave.reason,
                         'start_date': sick_leave.start_date_sick_leave.strftime('%d/%m/%Y'),
                         'end_date': sick_leave.end_date_sick_leave.strftime('%d/%m/%Y')}
                        for sick_leave in employee.sickleave_set.all()],
    }

    response = JsonResponse(employee_data, json_dumps_params={'indent': 4, 'ensure_ascii': False})

    filename = f'{employee.last_name}.json'
    response['Content-Disposition'] = f'attachment; filename="{quote(filename)}"'
    return response


@login_required(login_url='hr_records:login')
def export_pdf(request, employee_id):
    from .models import Employee, Vacation, BusinessTrip, SickLeave

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        raise Http404('Сотрудник не найден')

    vacations = Vacation.objects.filter(employee_vacation=employee).order_by('-start_date_vacation')
    business_trips = BusinessTrip.objects.filter(employee_business_trip=employee).order_by('-start_date_business_trip')
    sick_leaves = SickLeave.objects.filter(employee_sick_leave=employee).order_by('-start_date_sick_leave')
    records = list(vacations) + list(business_trips) + list(sick_leaves)

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=portrait(letter))

    pdfmetrics.registerFont(TTFont('Arial', 'hr_records/fonts/ArialRegular.ttf'))

    c.setFont('Arial', 12)

    # Информация о сотруднике
    c.drawString(50, 750, f'Сотрудник: {employee.last_name} {employee.first_name}')
    c.drawString(50, 730, f'Должность: {employee.position}')
    c.drawString(50, 710, f'Дата приема на работу: {employee.hire_date.strftime("%d/%m/%Y")}')
    c.drawString(50, 690, f'Email: {employee.email}')
    c.drawString(50, 670, f'Номер телефона: {employee.phone_number}')

    # Начальные координаты для текста об отпусках
    y = 650

    for record in records:
        if y <= 50:
            # Новая страницу
            c.showPage()
            c.setFont('Arial', 12)
            y = 750

        if isinstance(record, Vacation):
            record_type = "Отпуск"
            start_date = record.start_date_vacation.strftime("%d/%m/%Y")
            end_date = record.end_date_vacation.strftime("%d/%m/%Y")
        elif isinstance(record, BusinessTrip):
            record_type = "Командировка"
            start_date = record.start_date_business_trip.strftime("%d/%m/%Y")
            end_date = record.end_date_business_trip.strftime("%d/%m/%Y")
        elif isinstance(record, SickLeave):
            record_type = "Больничный"
            start_date = record.start_date_sick_leave.strftime("%d/%m/%Y")
            end_date = record.end_date_sick_leave.strftime("%d/%m/%Y")
        else:
            record_type = "Неизвестный тип"
            start_date = ""
            end_date = ""

        c.drawString(50, y, f'{record_type}: {start_date} - {end_date}')
        y -= 20

    c.save()

    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True, filename=f'{employee.last_name}.pdf')
    return response

