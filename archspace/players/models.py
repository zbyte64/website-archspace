from django.db import models
from django.contrib.auth.models import User

from game.models import Game
from race.models import Race

from signals import power

CONCENTRATION_MODES = [
    ('B', 'Balance'),
    ('I', 'Industry'),
    ('M', 'Military'),
    ('R', 'Research'),
]

class Player(models.Model):
    user = models.OneToOneField(User)
    game = models.ForeignKey(Game, related_name='players')
    race = models.ForeignKey(Race)
    empire_name = models.CharField(max_length=20, unique=True)
    
    production_points = models.PositiveIntegerField()
    honor = models.SmallIntegerField()
    concentration_mode = models.CharField(choices=CONCENTRATION_MODES, max_length=1)
    
    def get_power(self):
        total = 0
        for listener, power in power.send(sender=type(self), player=self):
            if power:
                total += power
        return total
    
    def __unicode__(self):
        return self.empire_name
