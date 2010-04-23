from rulebuilder.conditions import Condition, Language
from rulebuilder.forms import ConditionForm

from django import forms

from players.language import PLAYER_LANGUAGE

class PlanetForm(ConditionForm):
    representation_string = u'Player has %(operator)s %(planets)s planets'
    operator = forms.ChoiceField(choices=[('eq','equal to'),
                                          ('gt','greater then'),
                                          ('lt','less then')])
    planets = forms.IntegerField()

class PlanetCondition(Condition):
    form = PlanetForm

    operations = {'eq': lambda x, y: x == y,
                  'gt': lambda x, y: x > y,
                  'lt': lambda x, y: x < y}

    def evaluate(self, context, node):
        planets = int(node['planets'])
        return self.operations[node['operator']](node['player'].planets.count(), planets)

PLAYER_LANGUAGE.add('planet', PlanetCondition)

