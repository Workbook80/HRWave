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
from django.http import HttpResponse  #


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
        'date_of_birth': employee.date_of_birth.strftime('%d/%m/%Y'),
        'place_of_birth': employee.place_of_birth,
        'passport_series': employee.passport_series,
        'passport_number': employee.passport_number,
        'passport_issued_by': employee.passport_issued_by,
        'passport_issued_date': employee.passport_issued_date.strftime('%d/%m/%Y'),
        'passport_departament_code': employee.passport_departament_code,
        'registration_address': employee.registration_address,
        'current_address': employee.current_address,
        'position': employee.position,
        'hire_date': employee.hire_date.strftime('%d/%m/%Y'),
        'email': employee.email,
        'phone_number': employee.phone_number,
        # Поля сотрудника
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
    c.drawString(50, 750, f'Карточка сотрудника: {employee.last_name} {employee.first_name}')
    c.drawString(50, 710, 'Информация о сотруднике:')
    c.drawString(50, 690, f'Имя: {employee.first_name}')
    c.drawString(50, 670, f'Фамилия: {employee.last_name}')
    c.drawString(50, 650, f'Отчество: {employee.middle_name}')
    c.drawString(50, 630, f'Дата рождения: {employee.date_of_birth.strftime("%d/%m/%Y")}')
    c.drawString(50, 610, f'Должность: {employee.position}')
    c.drawString(50, 590, f'Дата приема на работу: {employee.hire_date.strftime("%d/%m/%Y")}')
    c.drawString(50, 570, f'Email: {employee.email}')
    c.drawString(50, 550, f'Номер телефона: {employee.phone_number}')
    c.drawString(50, 510, 'Паспортные данные:')
    c.drawString(50, 490, f'Серия паспорта: {employee.passport_series}')
    c.drawString(50, 470, f'Номер паспорта: {employee.passport_number}')
    c.drawString(50, 450, f'Паспорт выдан: {employee.passport_issued_by}')
    c.drawString(50, 430, f'Дата выдачи паспорта: {employee.passport_issued_date.strftime("%d/%m/%Y")}')
    c.drawString(50, 410, f'Код подразделения: {employee.passport_departament_code}')
    c.drawString(50, 390, f'Место рождения: {employee.place_of_birth}')
    c.drawString(50, 370, f'Адрес регистрации: {employee.registration_address}')
    c.drawString(50, 350, f'Адрес проживания: {employee.current_address}')
    c.drawString(50, 310, 'Связанные документы:')

    # Начальные координаты для текста об отпусках
    y = 290

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
            if record.type_vacation:
                record_info = record.type_vacation
            else:
                record_info = 'Нет данных'
        elif isinstance(record, BusinessTrip):
            record_type = "Командировка"
            start_date = record.start_date_business_trip.strftime("%d/%m/%Y")
            end_date = record.end_date_business_trip.strftime("%d/%m/%Y")
            if record.destination:
                record_info = record.destination
            else:
                record_info = 'Нет данных'
        elif isinstance(record, SickLeave):
            record_type = "Больничный"
            start_date = record.start_date_sick_leave.strftime("%d/%m/%Y")
            end_date = record.end_date_sick_leave.strftime("%d/%m/%Y")
            if record.reason:
                record_info = record.reason
            else:
                record_info = 'Нет данных'
        else:
            record_type = 'Неизвестный тип'
            start_date = ''
            end_date = ''
            record_info = ''

        c.drawString(50, y, f'{record_type}: {start_date} - {end_date} ({record_info})')
        y -= 20

    c.save()

    buffer.seek(0)
    response = FileResponse(buffer, as_attachment=True, filename=f'{employee.last_name}.pdf')
    return response


@login_required(login_url='hr_records:login')
def vacation_pdf(request):

    search_query = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Проверяем, есть ли значения year и month, и преобразуем их в числа
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None

    # Создаем queryset для модели Vacation с использованием Q-объектов
    vacation_query = Q()

    if search_query:
        vacation_query &= Q(employee_vacation__last_name__icontains=search_query)

    if year:
        vacation_query &= (Q(start_date_vacation__year=year) | Q(end_date_vacation__year=year))

    if month:
        vacation_query &= (Q(start_date_vacation__month=month) | Q(end_date_vacation__month=month))

    # Получите записи отпусков, соответствующие вашему запросу
    vacation_records = Vacation.objects.filter(vacation_query)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="records.pdf"'

    # Создаем PDF-документ с помощью библиотеки ReportLab
    c = canvas.Canvas(response, pagesize=letter)

    pdfmetrics.registerFont(TTFont('Arial', 'hr_records/fonts/ArialRegular.ttf'))

    c.setFont('Arial', 12)

    y = 750

    for record in vacation_records:
        if y <= 50:
            # Новая страницу
            c.showPage()
            c.setFont('Arial', 12)
            y = 750

        c.drawString(50, y, f'Сотрудник: {record.employee_vacation.last_name} {record.employee_vacation.first_name}')
        y -= 20
        c.drawString(50, y, f'Дата начала отпуска: {record.start_date_vacation.strftime("%d/%m/%Y")}')
        y -= 20
        c.drawString(50, y, f'Дата окончания отпуска: {record.end_date_vacation.strftime("%d/%m/%Y")}')
        y -= 20
        c.drawString(50, y, f'Вид отпуска: {record.type_vacation}')
        y -= 40

    c.save()
    return response


@login_required(login_url='hr_records:login')
def business_trip_pdf(request):

    search_query = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Проверяем, есть ли значения year и month, и преобразуем их в числа
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None

    # Создаем queryset для модели Vacation с использованием Q-объектов
    business_trip_query = Q()

    if search_query:
        business_trip_query &= Q(employee_business_trip__last_name__icontains=search_query)

    if year:
        business_trip_query &= (Q(start_date_business_trip__year=year) | Q(end_date_business_trip__year=year))

    if month:
        business_trip_query &= (Q(start_date_business_trip__month=month) | Q(end_date_business_trip__month=month))

    business_trip_records = BusinessTrip.objects.filter(business_trip_query)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="records.pdf"'

    # Создаем PDF-документ с помощью библиотеки ReportLab
    c = canvas.Canvas(response, pagesize=letter)

    pdfmetrics.registerFont(TTFont('Arial', 'hr_records/fonts/ArialRegular.ttf'))

    c.setFont('Arial', 12)

    y = 750

    for record in business_trip_records:
        if y <= 50:
            # Новая страницу
            c.showPage()
            c.setFont('Arial', 12)
            y = 750

        c.drawString(50, y,
                     f'Сотрудник: {record.employee_business_trip.last_name} {record.employee_business_trip.first_name}')
        y -= 20
        c.drawString(50, y, f'Дата начала командировки: {record.start_date_business_trip.strftime("%d/%m/%Y")}')
        y -= 20
        c.drawString(50, y, f'Дата окончания командировки: {record.end_date_business_trip.strftime("%d/%m/%Y")}')
        y -= 20
        if record.destination:
            c.drawString(50, y, f'Место назначения: {record.destination}')
        else:
            c.drawString(50, y, 'Место назначения: Неизвестно')
        y -= 40

    c.save()
    return response


@login_required(login_url='hr_records:login')
def sick_leave_pdf(request):

    search_query = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Проверяем, есть ли значения year и month, и преобразуем их в числа
    year = int(year) if year and year.isdigit() else None
    month = int(month) if month and month.isdigit() else None

    sick_leave_query = Q()

    if search_query:
        sick_leave_query &= Q(employee_sick_leave__last_name__icontains=search_query)

    if year:
        sick_leave_query &= (Q(start_date_sick_leave__year=year) | Q(end_date_sick_leave__year=year))

    if month:
        sick_leave_query &= (Q(start_date_sick_leave__month=month) | Q(end_date_sick_leave__month=month))

    # Получите записи отпусков, соответствующие вашему запросу
    sick_leave_records = SickLeave.objects.filter(sick_leave_query)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="records.pdf"'

    # Создаем PDF-документ с помощью библиотеки ReportLab
    c = canvas.Canvas(response, pagesize=letter)

    pdfmetrics.registerFont(TTFont('Arial', 'hr_records/fonts/ArialRegular.ttf'))

    c.setFont('Arial', 12)

    y = 750

    for record in sick_leave_records:
        if y <= 50:
            # Новая страницу
            c.showPage()
            c.setFont('Arial', 12)
            y = 750

        c.drawString(50, y,
                     f'Сотрудник: {record.employee_sick_leave.last_name} {record.employee_sick_leave.first_name}')
        y -= 20
        c.drawString(50, y, f'Дата начала больничного: {record.start_date_sick_leave.strftime("%d/%m/%Y")}')
        y -= 20
        c.drawString(50, y, f'Дата окончания больничного: {record.end_date_sick_leave.strftime("%d/%m/%Y")}')
        y -= 20
        c.drawString(50, y, f'Причина: {record.reason}')
        y -= 40

    c.save()
    return response
