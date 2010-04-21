from django.db import models

from player.models import Player

class TechnologyCategory(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class Technology(models.Model):
    name = models.CharField(max_length=30, unique=True)
    category = models.ForeignKey(TechnologyCategory, related_name='technologies')
    level = models.SmallPositiveIntegerField()
    description = models.TextField()
    
    def get_research_cost(self):
        return self.level * 50000
    
    def __unicode__(self):
        return self.name

class ResearchedTechnology(models.Model):
    player = models.ForeignKey(Player)
    technology = models.ForeignKey(Technology)

class Research(models.Model):
    player = models.OneToOneField(Player)
    technology = models.ForeignKey(Technology, blank=True, null=True)
    progress = models.PositiveIntegerField()
    
    def get_power(self):
        raise NotImplementedError
