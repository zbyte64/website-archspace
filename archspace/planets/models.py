import math
from random import randint
from django.db import models

from players.models import Player
from controlmodel.models import Environment, ControlModel
from controlmodel.signals import control_model
from rulebuilder.fields import RuleSetField
from language import PLANET_LANGUAGE

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

class PlanetaryAttribute(ControlModel):
    name = models.CharField(max_length=20, unique=True)
    terraform_points = models.PositiveIntegerField(default=0, help_text='The amount of terraforming points needed to remove attribute, 0 = cannot remove')
    description = models.TextField()
    terraform_requirements = RuleSetField(language=PLANET_LANGUAGE)
    
    def __unicode__(self):
        return self.name

class Nebula(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class PlanetManager(models.Manager):
    def cumulative_points(self):
        ret = dict()
        for index, planet in enumerate(self.all()):
            for key, value in planet.get_point_breakdown():
                if index == 0:
                    ret[key] = 0
                ret[key] += value
        return ret
    
    def discover_planet(self, player):
        planet = Planet(player=player)
        planet.nebula = player.planets.order_by('?')[0].nebula
        planet.randomize()
        planet.save()
        return planet
    
    def create_home_planet(self, player):
        assert player.planets.count() == 0, 'Player already has home planet'
        planet = Planet(player=player)
        planet.nebula = Nebula.objects.order_by('?')[0]
        for key, value in player.race.get_environment():
            setattr(planet, key, value)
        planet.save()
        return planet

class Planet(Environment):
    player = models.ForeignKey(Player, related_name='planets')
    nebula = models.ForeignKey(Nebula, related_name='planets')
    
    population = models.PositiveIntegerField(default=1000)
    size = models.PositiveSmallIntegerField(choices=PLANET_SIZES, default=3)
    resource = models.PositiveSmallIntegerField(choices=RESOURCE_TYPES, default=2)
    
    factories = models.PositiveIntegerField(default=10)
    research_labs = models.PositiveIntegerField(default=10)
    military_bases = models.PositiveIntegerField(default=10)    
    
    attributes = models.ManyToManyField(PlanetaryAttribute, blank=True)
    
    factory_ratio = models.PositiveSmallIntegerField(default=30)
    research_ratio = models.PositiveSmallIntegerField(default=20)
    military_ratio = models.PositiveSmallIntegerField(default=20)
    
    terraform_points = models.PositiveIntegerField(default=0)
    
    commerce_with = models.ManyToManyField('Planet', blank=True)
    
    objects = PlanetManager()
    
    ATMOSPHERE_TERRAFORM_COST = 5000
    
    def randomize(self):
        """
        Randomly selects the size, resource, atmo, and attributes of the planet
        """
        self.size = randint(1,5)
        self.resource = randint(1,3)
        self.temperature = randint(20, 1000)
        self.gravity = randint(0, 10)
        for key in self.get_atmosphere().keys():
            setattr(self, key, randint(0, 5))
        for attribute_count in range(randint(0, 3)):
            pa = PlanetaryAttribute.objects.order_by('?')[0]
            self.attributes.add(pa)
    
    def terraform(self):
        for attribute in self.attributes.all():
            if (attribute.terraform_points and
                attribute.terraform_points <= self.terraform_points and
                attribute.terraform_requirements.evaluate({'player':self.player, 'planet':self})):
                self.attributes.remove(attribute)
                self.terraform_points -= attribute.terraform_points
        for key, target in self.player.race.get_atmosphere():
            current = getattr(self, key, 0)
            delta = target - current
            if not delta: continue
            change = min(abs(change), self.terraform_points/ abs(change)*self.ATMOSPHERE_TERRAFORM_COST)
            self.terraform_points -= change * self.ATMOSPHERE_TERRAFORM_COST
            if delta < 0:
                setattr(self, key, target-change)
            else:
                setattr(self, key, target+change)
        #TODO gravity, temperature
    
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
    
    def get_commerce(self):
        total = 0
        
        control_model = self.get_log_control_model()
        self_pp = self.get_point_breakdown()['pp']
        
        for planet in self.commerce_with.all():
            other_pp = planet.get_point_breakdown()['pp']
            pp = (other_pp + self_pp) / 4
            total += pp * control_model['commerce']
        return total
    
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
        for attribute in self.attributes.all():
            cm.update(attribute.get_control_model())
        control_model.send(sender=type(self), instance=self, cm=cm)
        return cm
    
    def __unicode__(self):
        return u'%s-%s' % (self.nebula, self.pk)
    
    class Meta:
        pass
