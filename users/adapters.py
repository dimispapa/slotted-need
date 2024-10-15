from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.models import EmailAddress
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        Invoked after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        logger.debug("pre_social_login called.")

        email = sociallogin.account.extra_data.get('email')
        logger.debug(f'pre_social_login: email:{email}')
        if not email:
            messages.error(
                request, "Unable to retrieve email from the social account.")
            raise ImmediateHttpResponse(redirect('social_account_error'))

        try:
            user = User.objects.get(email=email)
            logger.debug(f'pre_social_login: user:{user}')
            logger.debug(
                f"Found user: {user.email}, is_active={user.is_active}")
            if not user.is_active:
                user.is_active = True
                user.save()
                logger.info(f"Activated user: {user.email}")
                messages.success(
                    request,
                    "Your account has been activated via Google OAuth.")

            # Mark the email as verified
            email_address, created = EmailAddress.objects.get_or_create(
                user=user, email=email)
            email_address.verified = True
            email_address.primary = True
            email_address.save()
            logger.debug(f"Marked email as verified for user: {user.email}")

            # Associate the social account with the existing user
            sociallogin.user = user
            logger.info(f"Associated social account with user: {user.email}")

        except User.DoesNotExist:
            logger.error("User does not exist; preventing signup.")
            messages.error(
                request,
                "No account found for this email. "
                "Please contact the administrator.")
            raise ImmediateHttpResponse(redirect('home'))

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Prevent automatic signup; only allow if user exists.
        """
        return False

    def populate_user(self, request, sociallogin, data):
        """
        Prevent Allauth from creating a new user; use the existing one.
        """
        return sociallogin.user

    def is_email_verified(self, provider, email):
        """
        Treat social account emails as verified.
        """
        return True
