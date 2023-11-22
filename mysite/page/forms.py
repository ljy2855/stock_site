from django import forms
from django.contrib.auth.models import User
from .models import *

# class PostForm(forms.ModelForm):

#     class Meta:
#         model = HoldingStock
#         fields = ('cnt',)
        
        
class UserForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('username','password',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'15자 이내로 입력 가능합니다.'}),
            'password' : forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': '닉네임',
            'password': '패스워드'
        }
        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__( *args, **kwargs)
            self.fields['username'].widget.attrs['maxlength'] = 15
            