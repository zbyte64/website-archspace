from django.db import models

class ControlModel(models.Model):
    environment = models.SmallIntegerField(help_text='The ability to terraform')
    production = models.SmallIntegerField(help_text='The ouput of factories')
    commerce = models.SmallIntegerField()
    diplomacy = models.SmallIntegerField()
    growth = models.SmallIntegerField()
    efficiency = models.SmallIntegerField()
    facility_cost = models.SmallIntegerField()
    research = models.SmallIntegerField()
    spy = models.SmallIntegerField()
    genius = models.SmallIntegerField()
    
    def get_control_model(self):
        cm = dict()
        for field in ControlModel._meta.fields:
            key = field.name
            cm[key] = getattr(self, key, 0)
        return cm
    
    class Meta:
        abstract = True

class Environment(models.Model):
    temperature = models.PositiveIntegerField()
    gravity = models.DecimalField(max_digits=4, decimal_places=2)
    
    hydrogen = models.PositiveSmallIntegerField()
    nitrogen = models.PositiveSmallIntegerField()
    oxygen = models.PositiveSmallIntegerField()
    water = models.PositiveSmallIntegerField()
    chlorine = models.PositiveSmallIntegerField()
    carbon_dioxide = models.PositiveSmallIntegerField()
    methane = models.PositiveSmallIntegerField()

    def get_atmosphere(self):
        raise NotImplementedError

    class Meta:
        abstract = True

