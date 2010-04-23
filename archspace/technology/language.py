from rulebuilder.conditions import Condition, Language
from rulebuilder.forms import ConditionForm

from django import forms

from models import Technology

from players.language import PLAYER_LANGUAGE

class TechnologyForm(ConditionForm):
    representation_string = u'Player has the following technology: %(tech)s'
    tech = forms.ModelChoiceField(Technology)

class TechnologyCondition(Condition):
    form = TechnologyForm

    def evaluate(self, context, node):
        races = node['tech']
        return context['player'].technologies.all().filter(pk=tech.pk).count()

PLAYER_LANGUAGE.add('tech', TechnologyCondition)

