from game.signals import turn
from players.signals import power

def on_turn(player, turn, **kwargs):
    """
    Take the mp available to the user minned with the build que investment
    substract from the investment
    progress the build que progress
    exchange progress for ship based on cost
    """
    for que in player.ship_build_ques.all():
        pass

turn.connect(on_turn)

def on_power(player, **kwargs):
    total_power = 0
    for fleet in player.fleets.all():
        total_power += fleet.get_power()
    for docking in player.docked_ships.all():
        total_power += docking.get_power()
    return total_power

power.connect(on_power)
