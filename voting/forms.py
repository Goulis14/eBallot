# voting/forms.py
import json
import os

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import inlineformset_factory
from django_countries.widgets import CountrySelectWidget

from eBallot import settings
from .models import CustomUser, Election, Candidate


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=CustomUser._meta.get_field('role').choices, required=True)
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES, required=True)
    age_group = forms.ChoiceField(choices=CustomUser.AGE_GROUPS, required=True)

    # We will set choices for these fields dynamically later
    country = forms.ChoiceField(choices=[], required=True)
    region = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role', 'gender', 'age_group', 'country', 'region']

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        # Load countries dynamically from a JSON file
        countries_data = []
        with open("static/data/countries+states.json", "r", encoding="utf-8") as f:
            countries_data = json.load(f)

        # Populate the 'country' dropdown with country names
        self.fields['country'].choices = [(country_data['name'], country_data['name'])
                                          for country_data in countries_data]

        # If the country is pre-selected, load regions for that country
        if 'country' in kwargs.get('data', {}):
            selected_country = kwargs['data']['country']
            for country_data in countries_data:
                if country_data['name'] == selected_country:
                    self.fields['region'].choices = [(region, region) for region in country_data['states']]
                    break


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
