from django.db import models

from utils import LayeredDict

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
        cm = LayeredDict()
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
        atmo = LayeredDict()
        for field in Environment._meta.fields:
            key = field.name
            if key in ('temperature', 'gavity'): continue
            atmo[key] = getattr(self, key, 0)
        return atmo

    def get_environment(self):
        enviro = LayeredDict()
        for field in Environment._meta.fields:
            key = field.name
            enviro[key] = getattr(self, key, 0)
        return enviro

    class Meta:
        abstract = True

class ControlStatInfo(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    
    def __unicode__(self):
        return self.name
