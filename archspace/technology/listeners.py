from game.signals import turn
from players.signals import power

def on_turn(player, turn, **kwargs):
    """
    Take the rp available to the user
    match rp with investment
    progress research
    """
    player.research

turn.connect(on_turn)

def on_power(player, **kwargs):
    total_power = 0
    for tech in player.technologies.all():
        total_power += tech.get_power()
    return total_power

power.connect(on_power)
