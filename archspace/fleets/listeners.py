from game.signals import turn

def on_turn(player, turn, **kwargs):
    for que in player.shipbuildques.all():
        pass

turn.connect(on_turn)
