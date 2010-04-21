import math
from django.db import models

from players.models import Player
from controlmodel.models import Environment

PLANET_SIZES = [
    (1, 'Tiny'),
    (2, 'Small'),
    (3, 'Medium'),
    (4, 'Large'),
    (5, 'Huge'),
]

RESOURCE_TYPES = [
    (1, 'Poor'),
    (2, 'Normal'),
    (3, 'Rich'),
]

ENVIRONMENTS = [
    (1, 'Suitable'),
    (3, 'Uncomfortable'),
    (5, 'Hostile'),
]

class PlanetaryAttribute(models.Model):
    name = models.CharField(max_length=20, unique=True)
    terraform_points = models.PositiveIntegerField(default=0, help_text='The amount of terraforming points needed to remove attribute, 0 = cannot remove')
    description = models.TextField()
    
    def __unicode__(self):
        return self.name

class Nebula(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Planet(Environment):
    player = models.ForeignKey(Player, related_name='planets')
    nebula = models.ForeignKey(Nebula, related_name='planets')
    
    population = models.PositiveIntegerField()
    size = models.PositiveSmallIntegerField(choices=PLANET_SIZES)
    resource = models.PositiveSmallIntegerField(choices=RESOURCE_TYPES)
    
    factories = models.PositiveIntegerField(default=0)
    research_labs = models.PositiveIntegerField(default=0)
    military_bases = models.PositiveIntegerField(default=0)    
    
    attributes = models.ManyToManyField(PlanetaryAttribute, blank=True)
    
    factory_ratio = models.PositiveSmallIntegerField()
    research_ratio = models.PositiveSmallIntegerField()
    military_ratio = models.PositiveSmallIntegerField()
    
    terraform_points = models.PositiveIntegerField()
    
    def get_environment_value(self):
        delta = 0
        for key, target in self.player.race.get_atmosphere():
            current = getattr(self, key, 0)
            delta += abs(target - current)
        #TODO factor in attributes
        return delta + 1
    
    @property
    def environment(self):
        delta = self.get_environment_value()
        for key, label in ENVIRONMENTS:
            if key <= delta: return label
        return label
    
    @property
    def max_population(self):
        return int(self.size * 100 / self.get_environment_value()) * 100000
    
    @property
    def buildings(self):
        return self.factories + self.research_labs + self.military_bases 
    
    def get_power(self):
        return self.nagoda_points()
    
    def get_nagoda_points(self):
        '''
        Nagoda is the raw energy the planet produces and is funelled into other products
        '''
        control_model = self.get_log_control_model()
        environment = max(self.get_environment_value(), 10)
        raw = self.population * self.resource / 2 / environment * self.buildings * control_model['efficiency'] 
        return raw
        
    def get_point_breakdown(self):
        raw = self.get_nagoda_points()
        
        environment = max(self.get_environment_value(), 10)
        control_model = self.get_log_control_model()
        
        growth_ratio = 1.0 - float(self.population) / self.max_population
        growth = growth_ratio * raw
        raw -= growth
        growth *= control_model['growth']
        
        building_ratio = 1.0 - float(self.buildings) / self.max_population
        build = building_ratio * raw
        raw -= build
        build *= control_model['growth']
        
        environment = max(self.get_environment_value(), 10)
        if environment >= 2:
            terraform_ratio = 1 - math.log(2, environment)
            terraform = terraform_retio * raw
            raw -= terraform
            terraform *= control_model['environment']
        else:
            terraform = 0
        
        pp = control_model['production'] * raw * self.factories / self.buildings
        rp = control_model['research'] * raw * self.research_labs / self.buildings
        mp = control_model['miliatry'] * raw * self.military_bases / self.buildings
        
        return {'growth':growth,
                'build':build,
                'terraform':terraform,
                'pp':pp,
                'rp':rp,
                'mp':mp,}
    
    def get_log_control_model(self):
        '''
        Return a control model dictionary that is logorthmically balanced
        Values must be greater than 0
        '''
        cm = self.get_control_model()
        for key, value in cm.items():
            cm[key] = math.log(max(value + 7, 2), 12)
        return cm
    
    def get_control_model(self):
        cm = self.player.get_control_model()
        #TODO apply planet cm modifiers
        return cm
    
    def __unicode__(self):
        return u'%s-%s' % (self.nebula, self.pk)
    
    class Meta:
        pass
