from __future__ import absolute_import

from django import forms
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.translation import pgettext, ugettext_lazy as _, ugettext
from allauth.account.forms import  SetPasswordField, PasswordField
from allauth.account.utils import perform_login, send_email_confirmation, setup_user_email
from allauth.account import app_settings
from verify.models import TwilioVerification
from parsley.decorators import parsleyfy
#from captcha.fields import ReCaptchaField

from userprofile.models import UserProfile


@parsleyfy
class SignupForm(forms.Form):
    username = forms.CharField(
        label = _("Username"),
        max_length = 30,
        min_length = app_settings.USERNAME_MIN_LENGTH,
        widget = forms.TextInput(attrs={'placeholder':_('Username') }))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':_('E-mail address') }))

    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))
    confirmation_key = forms.CharField(
        max_length = 40,
        required = False,
        widget = forms.HiddenInput())
    cell_phone = forms.RegexField(regex=r'^\+?1?\d{9,15}$', label=_("Cell Phone"),
                                error_message = ("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    terms_and_condition = forms.BooleanField(required = True)
    #captcha = ReCaptchaField()

    # def __init__(self, *args, **kwargs):
    #     kwargs['email_required'] = app_settings.EMAIL_REQUIRED
    #     super(SignupForm, self).__init__(*args, **kwargs)
    #     if not app_settings.SIGNUP_PASSWORD_VERIFICATION:
    #         del self.fields["password2"]
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists.', code='invalid')
        return email    

    def clean(self):
        super(SignupForm, self).clean()
        
        if app_settings.SIGNUP_PASSWORD_VERIFICATION \
                and "password1" in self.cleaned_data \
                and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        user_profile_obj = UserProfile.objects.filter(cell_phone=self.cleaned_data['cell_phone'])
        if user_profile_obj:
                raise forms.ValidationError(_("Sorry. This cell phone number is already associated with a 24/7Mixtapes account. Please try again"))
        return self.cleaned_data

    # def create_user(self, commit=True):
    #     user = super(SignupForm, self).create_user(commit=False)
    #     password = self.cleaned_data.get("password1")
    #     if password:
    #         user.set_password(password)
    #     if commit:
    #         user.save()
    #    return user

    def save(self, request): 
                 
        # new_user = self.create_user()
        # super(SignupForm, self).save(new_user)
        # setup_user_email(request, new_user, [])
        self.after_signup(request)
        return request

    def after_signup(self, user, **kwargs):
        """
        An extension point for subclasses.
        """
        pass