from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from players.models import Player, Race

WEAPON_TYPES = [
    ('B', 'Beam'),
    ('M', 'Missile'),
    ('P', 'Projectile'),
]

ARMOR_TYPES = [
    ('N', 'Normal'),
    ('B', 'Bio'),
    ('R', 'React'),
]

class ShipSize(models.Model):
    name = models.CharField(max_length=20, unique=True)
    weapon_slots = models.PositiveSmallIntegerField()
    weapon_space = models.PositiveIntegerField(help_text='Space per weapon slot')
    device_slots = models.PositiveSmallIntegerField()
    hit_points = models.PositiveIntegerField()
    building_cost = models.PositiveIntegerField()
    
    def get_weapon_count(self, weapon):
        return int(self.weapon_size / weapon.space)
    
    def __unicode__(self):
        return self.name

class ShipComponent(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        abstract = True

class Weapon(ShipComponent):
    type = models.CharField(choices=WEAPON_TYPES, max_length=1)
    min_damage = models.PositiveIntegerField()
    max_damage = models.PositiveIntegerField()
    cooling_time = models.PositiveIntegerField()
    range = models.PositiveIntegerField()
    angle = models.PositiveIntegerField()
    attack_rate = models.PositiveIntegerField()
    space = models.PositiveIntegerField()

class Armor(ShipComponent):
    type = models.CharField(choices=ARMOR_TYPES, max_length=1)
    
    damage_resistance = models.PositiveSmallIntegerField()
    hp_multiplier = models.DecimalField(max_digits=4, decimal_places=2)

class Device(ShipComponent):
    level = models.PositiveSmallIntegerField()

class Computer(ShipComponent):
    level = models.PositiveSmallIntegerField()
    
class Engine(ShipComponent):
    level = models.PositiveSmallIntegerField()

class Shield(ShipComponent):
    level = models.PositiveSmallIntegerField()

class ShipDesign(models.Model):
    player = models.ForeignKey(Player, related_name='ship_designs')
    name = models.CharField(max_length=50)
    
    size = models.ForeignKey(ShipSize)
    armor = models.ForeignKey(Armor)
    computer = models.ForeignKey(Computer)
    engine = models.ForeignKey(Engine)
    shield = models.ForeignKey(Shield)
    
    weapons = models.ManyToManyField(Weapon)
    devices = models.ManyToManyField(Device, blank=True)
    
    def get_power(self):
        raise NotImplementedError
    
    def __unicode__(self):
        return self.name

class CommanderAttribute(models.Model):
    name = models.CharField(max_length=20, unique=True)
    races = models.ManyToManyField(Race)

    def __unicode__(self):
        return self.name

class Commander(models.Model):
    player = models.ForeignKey(Player, related_name='commanders')
    name = models.CharField(max_length=50)
    
    level = models.PositiveSmallIntegerField()
    experience = models.PositiveIntegerField()
    fleet_commanding = models.PositiveIntegerField()
    efficiency = models.PositiveIntegerField()
    
    offensive = models.PositiveSmallIntegerField()
    defensive = models.PositiveSmallIntegerField()
    maneuver = models.PositiveSmallIntegerField()
    detection = models.PositiveSmallIntegerField()
    
    armada_efficiency = models.SmallIntegerField()
    armada_offensive = models.SmallIntegerField()
    armada_defensive = models.SmallIntegerField()
    
    attributes = models.ManyToManyField(CommanderAttribute, blank=True)

    def __unicode__(self):
        return self.name

class Fleet(models.Model):
    name = models.CharField(max_length=30)
    player = models.ForeignKey(Player, related_name='fleets')
    ship_design = models.ForeignKey(ShipDesign)
    experience = models.PositiveSmallIntegerField()
    ships = models.PositiveSmallIntegerField()
    commander = models.OneToOneField(Commander)

    @property
    def status(self):
        if self.mission:
            return self.mission.label
        return u'Stand-by'
    
    @property
    def mission(self):
        try:
            return self.fleetmission.mission
        except ObjectDoesNotExist:
            return None
    
    def get_power(self):
        return self.ship_design.get_power() * self.ships
    
    def __unicode__(self):
        return self.name

class ShipDock(models.Model):
    player = models.ForeignKey(Player)
    ship_design = models.ForeignKey(ShipDesign)
    ships = models.PositiveIntegerField()
    
    def get_power(self):
        return self.ship_design.get_power() * self.ships
    
    class Meta:
        unique_together = [('player', 'ship_design')]

class ShipBuildQue(models.Model):
    player = models.ForeignKey(Player, related_name='shipbuildques')
    ship_design = models.ForeignKey(ShipDesign)
    ships = models.PositiveIntegerField()
    order = models.PositiveSmallIntegerField()
    
    progress = models.PositiveIntegerField()
    
    class Meta:
        unique_together = [('player', 'order')]
        ordering = ['order']
    
