from django.db import models

from fleets.models import Fleet
from planets.models import Planet
from players.models import Player

from signals import mission_expire

MISSION_TYPES = [
    ('SD', 'Stationed'),
    ('EX', 'Expidition'),
    ('RE', 'Returning'),
    ('PA', 'Patrol'),
    ('DI', 'Dispatched to Ally'),
    ('TR', 'Train'),
    ('SI', 'Siege'),
    ('BL', 'Blockade'),
    ('RA', 'Raid'),
    ('PR', 'Privateer')
]

class FleetMission(models.Model):
    fleet = models.OneToOneField(Fleet)
    mission = models.ForeignKey('Mission')

class Mission(models.Model):
    type = models.CharField(choices=MISSION_TYPES, max_length=2)
    expire_turn = models.PositiveIntegerField()
    player = models.ForeignKey(Player, related_name='missions') #for quick look ups
    fleets = models.ManyToManyField(Fleet, through=FleetMission)
    target = models.ForeignKey(Planet, blank=True, null=True)
    
    def expire(self):
        mission_expire.send(sender=type(self), mission=self)
        self.delete()
    
    @property
    def label(self):
        return dict(MISSION_TYPES)[self.type]

class MissionWithFormation(Mission):
    formation = models.TextField() #store as yaml
    armada_leader = models.ForeignKey(Fleet)
