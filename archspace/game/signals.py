from django.dispatch import Signal

turn = Signal(providing_args=["player", "turn"])
