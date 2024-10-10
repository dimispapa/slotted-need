from factory import django, Sequence, PostGenerationMethodCall
from django.contrib.auth.models import User


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'user{n}')
    # password = django.Password('test_pass')
    # Use 'PostGenerationMethodCall' to set the password,
    # after the user is created
    password = PostGenerationMethodCall('set_password', 'testpass')
