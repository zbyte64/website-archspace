from game.signals import turn
from players.signals import power
from players.models import Player
from django.db.models.signals import post_save

def on_turn(player, turn, **kwargs):
    """
    do terraform
    collect pp
    """
    for planet in player.planets.all():
        points = planet.get_point_breakdown()
        planet.terraform_points += points['terraform']
        planet.terraform()
        player.production_points += planet['pp']
        planet.save()

turn.connect(on_turn)

def on_power(player, **kwargs):
    total_power = 0
    for planet in player.planets.all():
        total_power += planet.get_power()
    return total_power

power.connect(on_power)

def create_home_planet(instance, created, **kwargs):
    if created:
        player.planets.create_home_planet(player)
    
post_save.connect(create_home_planet, sender=Player)
