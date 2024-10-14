from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Disable standard signups
        return False


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already logged in, do nothing
        if request.user.is_authenticated:
            return

        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')

        if not email:
            # If no email is provided by the social account, prevent signup
            messages.error(request, 'No email provided by social account.')
            raise ValidationError('No email provided by social account.')

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                # User is invited but not active,
                # allow them to log in via social account
                sociallogin.connect(request, user)
            else:
                # User is active, allow login
                pass
        except User.DoesNotExist:
            # Email not found in the system, prevent signup
            messages.error(request, 'You are not authorized to sign up. '
                           'Please contact the administrator.')
            raise ValidationError('You are not authorized to sign up.')
