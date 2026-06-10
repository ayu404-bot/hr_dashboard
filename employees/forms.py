from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        # Tells Django to automatically include all fields from models.py
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This loop styles every single input box to match your attractive dark theme
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input ms-2'})
            else:
                field.widget.attrs.update({
                    'style': 'background-color: #171a21 !important; border: 1px solid #2b303c; color: #ffffff !important; border-radius: 8px;',
                    'class': 'form-control mb-3 p-2'
                })