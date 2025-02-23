# voting/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from django_countries.widgets import CountrySelectWidget
from .models import CustomUser, Election, Candidate


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices, required=True)
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)  # Added gender field
    age_group = forms.ChoiceField(choices=CustomUser.AGE_GROUPS, required=True)    # Added age_group field
    country = forms.ChoiceField(choices=[], required=False)
    region = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'gender', 'age_group', 'country', 'region']


class ElectionForm(forms.ModelForm):
    ACTIVE_CHOICES = [
        (True, 'Active'),
        (False, 'Not Active'),
    ]

    is_active = forms.ChoiceField(
        choices=ACTIVE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="Status"
    )

    active_from = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        required=False,
        label="Active From (optional)"
    )

    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'is_active', 'active_from']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter a brief description'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter election title'}),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter candidate name'}),
        }


# Inline formset for Candidate
CandidateFormSet = inlineformset_factory(
    Election, Candidate, form=CandidateForm, extra=2, min_num=2, validate_min=True, can_delete=True
)
