from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory

from .models import CustomUser, Election, Candidate


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter a brief description of the election',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter election title',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter candidate name',
            }),
        }


# Inline formset for Candidate
CandidateFormSet = inlineformset_factory(
    Election, Candidate, form=CandidateForm, extra=1, can_delete=True
)
