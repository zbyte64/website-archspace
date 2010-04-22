from rulebuilder.conditions import Condition, IfCondition, Language
from ruleduilder.forms import ConditionForm

from django import forms

from race.models import Race
from technology.models import Technology

class RaceForm(ConditionForm):
    representation_string = u'Player is the following race: %(races)s'
    races = forms.ModelMultipleChoiceField(Race)

class RaceCondition(Condition):
    form = RaceForm

    def evaluate(self, context, node):
        races = node['races']
        return context['player'].race in races

class TechnologyForm(ConditionForm):
    representation_string = u'Player has the following technology: %(tech)s'
    tech = forms.ModelChoiceField(Technology)

class TechnologyCondition(Condition):
    form = TechnologyForm

    def evaluate(self, context, node):
        races = node['tech']
        return context['player'].technologies.all().filter(pk=tech.pk).count()

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

class PowerForm(ConditionForm):
    representation_string = u"Player's is %(operator)s %(power)s"
    operator = forms.ChoiceField(choices=[('eq','equal to'),
                                          ('gt','greater then'),
                                          ('lt','less then')])
    power = forms.IntegerField()

class PowerCondition(Condition):
    form = PowerForm

    operations = {'eq': lambda x, y: x == y,
                  'gt': lambda x, y: x > y,
                  'lt': lambda x, y: x < y}

    def evaluate(self, context, node):
        power = int(node['power'])
        return self.operations[node['operator']](node['player'].get_power(), power)

def build_player_language():
    lang = Language()
    lang.add('if', IfCondition)
    lang.add('race', RaceCondition)
    land.add('tech', TecchnologyCondition)
    lang.add('planet', PlanetCondition)
    land.add('power', PowerCondition)
    return lang
    
