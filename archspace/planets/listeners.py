from game.signals import turn

def on_turn(player, turn, **kwargs):
    for planet in player.planets.all():
        pass

turn.connect(on_turn)
