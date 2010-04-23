from django.db import models

from players.models import Player
from players.language import PLAYER_LANGUAGE
from rulebuilder.fields import RuleSetField

class TechnologyCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class Technology(models.Model):
    name = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(TechnologyCategory, related_name='technologies')
    level = models.PositiveSmallIntegerField()
    description = models.TextField()
    requirements = RuleSetField(language=PLAYER_LANGUAGE)
    
    players = models.ManyToManyField(Player, through='ResearchedTechnology', related_name='technologies')
    
    def get_research_cost(self):
        return self.level * 50000
    
    def get_power(self):
        return self.get_research_cost()
    
    def __unicode__(self):
        return self.name

class ResearchedTechnology(models.Model):
    player = models.ForeignKey(Player)
    technology = models.ForeignKey(Technology)

class Research(models.Model): #CONSIDER, create a research que to be more realistic
    player = models.OneToOneField(Player)
    technology = models.ForeignKey(Technology, blank=True, null=True)
    progress = models.PositiveIntegerField()
    investment = models.PositiveIntegerField()
    
    def get_power(self):
        raise NotImplementedError
