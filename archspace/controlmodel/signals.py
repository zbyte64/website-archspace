from django.dispatch import Signal

#TODO make into a prioritizing signal processor
control_model = Signal(providing_args=["instance", "cm"])
control_model.__doc__ = """
cm is a dictionary that gets passed through the listeners and the listeners may
choose to modify the cm
"""
