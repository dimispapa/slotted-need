from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_invitation_email(user, request):
    """
    Sends an invitation email to the user for setting up their account.

    Args:
        user (User): The user instance to send the invitation to.
        request (HttpRequest): The current HTTP request.

    Returns:
        tuple: (success: bool, error: Exception or None)
    """
    try:
        # Ensure the user has a primary key
        if not user.pk:
            raise ValueError(
                "User must be saved before sending invitation email.")

        # Generate token and uidb64
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Construct confirmation URL
        protocol = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        confirmation_url = f"{protocol}://{domain}{reverse(
            'account_setup_confirm',
            kwargs={'uidb64': uidb64, 'token': token})}"

        # Render email subject and body
        subject = render_to_string('users/account_setup_subject.txt',
                                   {'site_name': domain})
        body = render_to_string('users/account_setup_email.html', {
            'user': user,
            'site_name': domain,
            'confirmation_url': confirmation_url,
        })

        # Send email
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(
            f"send_invitation_email: Invitation email sent to {user.email}.")

        return True, None

    except Exception as e:
        logger.error(
            f"send_invitation_email: Error sending email to {user.email}: {e}")
        return False, e
