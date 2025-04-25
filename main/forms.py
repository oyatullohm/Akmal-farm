from django import forms
from .models import CustomUser

from django.core.validators import RegexValidator

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=13,
        label="Telefon raqamingiz",
        validators=[
            RegexValidator(
                regex=r"^\+998\d{9}$",
                message=" +998XXXXXXXXX formatida kiriting",
            )
        ],
    )
    is_agreed = forms.BooleanField(
        required=True,
        label="Foydalanish shartlariga roziman"
    )

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=4, label="Tasdiqlash kodi")

class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']
        labels = {
            'first_name': 'Ismingiz',
            'last_name': 'Familiyangiz'
        }
