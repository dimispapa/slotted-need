from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import (UserCreationForm
                                       as DjangoUserCreationForm,
                                       )


class CustomUserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(required=True)
    is_staff = forms.BooleanField(required=False, label='Admin Status')
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Groups'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1',
                  'password2', 'is_staff', 'groups')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = self.cleaned_data['is_staff']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
        return user
