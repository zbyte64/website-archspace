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

class PlanetPopulationForm(ConditionForm):
    representation_string = u'Planet has %(operator)s %(population)s population'
    operator = forms.ChoiceField(choices=[('eq','equal to'),
                                          ('gt','greater then'),
                                          ('lt','less then')])
    population = forms.IntegerField()

class PlanetPopulationCondition(Condition):
    form = PlanetPopulationForm

    operations = {'eq': lambda x, y: x == y,
                  'gt': lambda x, y: x > y,
                  'lt': lambda x, y: x < y}

    def evaluate(self, context, node):
        population = int(node['population'])
        return self.operations[node['operator']](node['planet'].population, population)

def build_planet_language():
    lang = Language(PLAYER_LANGUAGE)
    lang.add('planetpopulation', PlanetPopulationCondition)
    return lang

PLANET_LANGUAGE = build_planet_language()

