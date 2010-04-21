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
    type = models.CharField(choice=WEAPON_TYPES, max_length=1)
    min_damage = models.PositiveIntegerField()
    max_damage = models.PositiveIntegerField()
    cooling_time = models.PositiveIntegerField()
    range = models.PositiveIntegerField()
    angle = models.PositiveIntegerField()
    attack_rate = models.PositiveIntegerField()
    space = models.PositiveIntegerField()

class Armor(ShipComponent):
    type = models.CharField(choice=ARMOR_TYPES, max_length=1)
    
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
    player = models.ForeignKey(Player)
    name = models.CharField(max_length=50)
    
    size = models.ForeignKey(ShipSize)
    armor = models.ForeignKey(Armor)
    computer = models.Foreignkey(Computer)
    engine = models.ForeignKey(Engine)
    shield = models.ForeignKey(Shield)
    
    weapons = models.ManyToManyField(Weapon)
    devices = models.ManyToManyField(Device, blank=True)
    
    def __unicode__(self):
        return self.name

class CommandeAttribute(models.Model):
    name = models.CharField(max_length=20, unique=True)
    races = models.ManyToManyField(Race)

    def __unicode__(self):
        return self.name

class Commander(models.model):
    player = models.ForeignKey(Player)
    name = models.CharField(max_length=50)
    
    level = models.PostiveSmallIntegerField()
    experience = models.PositiveIntegerField()
    fleet_commanding = models.PositiveIntegerField()
    efficiency = models.PositiveIntegerField()
    
    offensive = models.SmallIntegerField()
    defensive = models.SmallIntegerField()
    maneuver = models.SmallintegerField()
    detection = models.SmallIntegerField()
    
    armada_efficiency = models.SmallIntegerField()
    armada_offensive = models.SmallIntegerField()
    armada_defensive = models.SmallIntegerField()
    
    attributes = models.ManyToManyField(CommanderAttribute, blank=True)

    def __unicode__(self):
        return self.name

class Fleet(models.Model):
    name = models.CharField(max_length=30)
    player = models.ForeignKey(Player)
    ship_design = models.ForeignKey(ShipDesign)
    experience = models.PositiveSmallIntegerField()
    ships = models.PositiveSmallIntegerField()
    commander = models.ForeignKey(Commander)

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
    
    def __unicode__(self):
        return self.name

