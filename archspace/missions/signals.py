from django.dispatch import Signal

mission_expire = Signal(providing_args=["mission"])
