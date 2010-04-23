from rulebuilder.conditions import Condition, IfCondition, Language
from rulebuilder.forms import ConditionForm

from django import forms

from race.models import Race

class RaceForm(ConditionForm):
    representation_string = u'Player is the following race: %(races)s'
    races = forms.ModelMultipleChoiceField(Race)

class RaceCondition(Condition):
    form = RaceForm

    def evaluate(self, context, node):
        races = node['races']
        return context['player'].race in races

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
    lang.add('power', PowerCondition)
    return lang

PLAYER_LANGUAGE = build_player_language()

