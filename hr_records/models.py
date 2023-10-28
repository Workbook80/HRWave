from django.db import models


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True, verbose_name='Идентификатор сотрудника')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=50, blank=True, verbose_name='Отчество')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    place_of_birth = models.CharField(max_length=50, verbose_name='Место рождения')
    passport_series = models.IntegerField(verbose_name='Серия паспорта')
    passport_number = models.IntegerField(verbose_name='Номер паспорта')
    passport_issued_by = models.CharField(max_length=50, verbose_name='Паспорт выдан')
    passport_issued_date = models.DateField(verbose_name='Дата выдачи')
    passport_departament_code = models.IntegerField(verbose_name='Код подразделения')
    registration_address = models.CharField(max_length=50, verbose_name='Адрес регистрации')
    current_address = models.CharField(max_length=50, verbose_name='Арес проживания')
    position = models.CharField(max_length=30, verbose_name='Должность')
    hire_date = models.DateField(verbose_name='Дата приема на работу')
    email = models.EmailField(blank=True, verbose_name='Почта')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Номер телефона')

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class Vacation(models.Model):
    vacation_id = models.AutoField(primary_key=True, verbose_name='Идентификатор отпуска')
    employee_vacation = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    type_vacation = models.CharField(max_length=50, blank=True, verbose_name='Вид отпуска')    # Новый атрибут
    start_date_vacation = models.DateField(verbose_name='Дата начала отпуска')
    end_date_vacation = models.DateField(verbose_name='Дата конца отпуска')

    def __str__(self):
        return f'{self.employee_vacation}: {self.start_date_vacation} - {self.end_date_vacation}'

    class Meta:
        verbose_name = 'Отпуск'
        verbose_name_plural = 'Отпуска'


class BusinessTrip(models.Model):
    business_trip_id = models.AutoField(primary_key=True, verbose_name='Идентификатор командировки')
    employee_business_trip = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    destination = models.CharField(max_length=50, blank=True, verbose_name='Место назначения')
    start_date_business_trip = models.DateField(verbose_name='Дата начала командировки')
    end_date_business_trip = models.DateField(verbose_name='Дата конца командировки')

    def __str__(self):
        return f'{self.employee_business_trip}: {self.start_date_business_trip} - {self.end_date_business_trip}'

    class Meta:
        verbose_name = 'Командировка'
        verbose_name_plural = 'Командировки'


class SickLeave(models.Model):
    sick_leave_id = models.AutoField(primary_key=True, verbose_name='Идентификатор больничного')
    employee_sick_leave = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    reason = models.CharField(max_length=50, blank=True, verbose_name='Причина')
    start_date_sick_leave = models.DateField(verbose_name='Дата начала больничного')
    end_date_sick_leave = models.DateField(verbose_name='Дата конца больничного')

    def __str__(self):
        return f'{self.employee_sick_leave}: {self.start_date_sick_leave} - {self.end_date_sick_leave}'

    class Meta:
        verbose_name = 'Больничный'
        verbose_name_plural = 'Больничные'


