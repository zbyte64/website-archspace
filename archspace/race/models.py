from django.db import models

from controlmodel.models import ControlModel, Environment

class Race(Environment, ControlModel):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

