from game.signals import turn

from models import Mission

def on_turn(player, turn, **kwargs):
    for mission in player.missions.filter(expire_turn__lte=turn):
        mission.expire()

turn.connect(on_turn)
