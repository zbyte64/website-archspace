from django.db import models
from django.contrib.sites.models import Site

from signals import turn

class Game(models.Model):
    turn = models.PositiveIntegerField(default=0)
    site = models.ForeignKey(Site)
    
    def do_turn(self):
        self.turn += 1
        for player in self.players:
            turn.send(sender=type(self), player=player, turn=self.turn)
        self.save()
