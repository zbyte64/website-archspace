from django.db import models
from django.contrib.auth.models import User

from game.models import Game
from race.models import Race
from controlmodel.models import ControlModel
from controlmodel.signals import control_model

from signals import power

class ConcentrationMode(ControlModel):
    name = models.CharField(max_length=20, unique=True)
    
    def __unicode__(self):
        return self.name

class Player(models.Model):
    user = models.OneToOneField(User)
    game = models.ForeignKey(Game, related_name='players')
    race = models.ForeignKey(Race)
    empire_name = models.CharField(max_length=20, unique=True)
    
    production_points = models.PositiveIntegerField()
    honor = models.SmallIntegerField()
    concentration_mode = models.ForeignKey(ConcentrationMode)
    
    def get_power(self):
        total = 0
        for listener, power in power.send(sender=type(self), player=self):
            if power:
                total += power
        return total
    
    def get_control_model(self):
        cm = self.race.get_control_model()
        cm.update(self.concentration_model.get_control_model())
        control_model.send(sender=type(self), instance=self, cm=cm)
        return cm
    
    def __unicode__(self):
        return self.empire_name
