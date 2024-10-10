from factory import (django, Sequence, PostGenerationMethodCall, Trait, Faker,
                     SubFactory)
from django.contrib.auth.models import User
from products.models import Product
from orders.models import Order, OrderItem


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f'user{n}')
    # Use 'PostGenerationMethodCall' to set the password,
    # after the user is created
    password = PostGenerationMethodCall('set_password', 'testpass')

    # Define params to vary the user instance if needed
    class Params:
        staff = Trait(is_staff=True)
        superuser = Trait(is_superuser=True)


class ProductFactory(django.DjangoModelFactory):
    class Meta:
        model = Product

    name = Sequence(lambda n: f"Product {n}")


class OrderFactory(django.DjangoModelFactory):
    class Meta:
        model = Order

    client_name = Faker('name')
    client_email = Faker('email')
    client_phone = Faker('phone_number')
    paid = Faker('boolean')


class OrderItemFactory(django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = SubFactory(OrderFactory)
    product = SubFactory(ProductFactory)
    item_value = Faker('random_int', min=50, max=500)
    item_status = Faker('random_int', min=1, max=4)
