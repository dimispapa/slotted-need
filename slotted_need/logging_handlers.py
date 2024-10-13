from django.utils.log import AdminEmailHandler
from datetime import datetime


class SimpleAdminEmailHandler(AdminEmailHandler):
    """
    A custom AdminEmailHandler that sends emails containing only the
    levelname and asctime, excluding the full error message and traceback.
    """

    def emit(self, record):
        """
        Overrides the default emit method to customize the email content.
        """
        # Format the asctime
        asctime = datetime.fromtimestamp(
            record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Create the email subject and message
        subject = f"SLOTTED NEED - {record.levelname} at {asctime}"
        message = (f"Error level:{record.levelname} detected at {asctime} "
                   "affecting the Slotted Need application\n\n"
                   "Check the Sentry log for full details on this error.")

        # Send the email
        self.send_mail(
            subject,
            message,
            fail_silently=True,
            html_message=None
        )
