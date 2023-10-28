from django import forms
from .models import Employee, Vacation, BusinessTrip, SickLeave


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk is None:
            self.fields['first_name'].initial = ''
            self.fields['last_name'].initial = ''
            self.fields['middle_name'].initial = ''
            self.fields['place_of_birth'].initial = ''
            self.fields['passport_series'].initial = ''
            self.fields['passport_number'].initial = ''
            self.fields['passport_issued_by'].initial = ''
            self.fields['passport_departament_code'].initial = ''
            self.fields['registration_address'].initial = ''
            self.fields['current_address'].initial = ''
            self.fields['position'].initial = ''
            self.fields['email'].initial = ''
            self.fields['phone_number'].initial = ''

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')
        first_name = cleaned_data.get('first_name')
        middle_name = cleaned_data.get('middle_name')
        position = cleaned_data.get('position')

        if last_name is not None:
            cleaned_data['last_name'] = last_name.capitalize()

        if first_name is not None:
            cleaned_data['first_name'] = first_name.capitalize()

        if middle_name is not None:
            cleaned_data['middle_name'] = middle_name.capitalize()

        if position is not None:
            cleaned_data['position'] = position.capitalize()

        return cleaned_data


class VacationForm(forms.ModelForm):
    class Meta:
        model = Vacation
        fields = ['type_vacation', 'start_date_vacation', 'end_date_vacation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверяем, редактируется ли существующий сотрудник
        if self.instance.pk is None:
            # Если создается новый сотрудник, устанавливаем значение полей по умолчанию
            self.fields['type_vacation'].initial = ''


class BusinessTripForm(forms.ModelForm):
    class Meta:
        model = BusinessTrip
        fields = ['destination', 'start_date_business_trip', 'end_date_business_trip']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверяем, редактируется ли существующий сотрудник
        if self.instance.pk is None:
            # Если создается новый сотрудник, устанавливаем значение полей по умолчанию
            self.fields['destination'].initial = ''


class SickLeaveForm(forms.ModelForm):
    class Meta:
        model = SickLeave
        fields = ['reason', 'start_date_sick_leave', 'end_date_sick_leave']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверяем, редактируется ли существующий сотрудник
        if self.instance.pk is None:
            # Если создается новый сотрудник, устанавливаем значение полей по умолчанию
            self.fields['reason'].initial = ''
