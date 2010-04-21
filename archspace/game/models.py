from django.db import models
from django.contrib.sites.models import Site

from signals import turn

class Game(models.Model):
    name = models.CharField(max_length=20)
    turn = models.PositiveIntegerField(default=0)
    turn_duration = models.PositiveSmallIntegerField(default=5, help_text='Number of minutes between turns')
    site = models.ForeignKey(Site)
    
    def do_turn(self):
        self.turn += 1
        for player in self.players:
            turn.send(sender=type(self), player=player, turn=self.turn)
        self.save()
    
    def __unicode__(self):
        return self.name
