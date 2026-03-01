from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

from .models import Group, Rating, Student, Survey


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Kullanıcı adınız'}),
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500', 'placeholder': 'Şifreniz'}),
    )


class AddStudentForm(forms.Form):
    first_name = forms.CharField(label='Ad', max_length=150)
    last_name = forms.CharField(label='Soyad', max_length=150)
    username = forms.CharField(label='Kullanıcı Adı', max_length=150)
    ogrenci_no = forms.CharField(label='Öğrenci No', max_length=50)
    group = forms.ModelChoiceField(label='Grup', queryset=Group.objects.all(), required=False, empty_label='Grup Yok')


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['lesson_name']
        labels = {'lesson_name': 'Ders Adı'}


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        labels = {'name': 'Grup Adı'}


class RatingForm(forms.Form):
    ratee_id = forms.IntegerField(widget=forms.HiddenInput())
    score = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(),
        label='Puan',
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Yorum (isteğe bağlı)'}),
        label='Yorum',
    )


class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_class = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500'
        self.fields['old_password'].widget.attrs.update({'class': field_class})
        self.fields['new_password1'].widget.attrs.update({'class': field_class})
        self.fields['new_password2'].widget.attrs.update({'class': field_class})
