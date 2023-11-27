from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.models import User
class UserRegistrationForm(forms.ModelForm):
    # User 模型的字段
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    # UserProfile 模型的字段
    telephone = forms.CharField(label='Telephone')
    resident_num = forms.CharField(label='Resident Identity Card Number')

    class Meta:
        model = User
        fields = ['username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()

            # 创建并保存 UserProfile 实例
            profile = UserProfile(user=user, telephone=self.cleaned_data['telephone'],
                                  resident_num=self.cleaned_data['resident_num'],
                                  balance=0)
            profile.save()
        return user
