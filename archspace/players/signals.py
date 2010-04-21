from django.dispatch import Signal

power = Signal(providing_args=["player"])

