#CONSIDER json allows for nesting, html forms not so much
#use auto_id=False to be safe

from django import forms
from django.forms.forms import BoundField
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

class ConditionForm(forms.Form):
    representation_string = ''
    prototype = forms.CharField(widget=forms.HiddenInput)
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language')
        json = kwargs.pop('json', None)
        key = kwargs.pop('key', None)
        if key:
            kwargs.setdefault('initial', {})
            kwargs['initial']['prototype'] = key
        super(ConditionForm, self).__init__(*args, **kwargs)
        if json:
            self.load_json(json)

    def clean_prototype(self):
        prototype = self.cleaned_data.get('prototype', None)
        if prototype and prototype not in self.language.operations:
            raise forms.ValidationError('Not a valid prototype')
        return prototype
    
    def load_json(self, data):
        if isinstance(data, basestring):
            data = json.loads(data)
        self.data = dict()
        prefix = ''
        if self.prefix:
            prefix = self.prefix + '-'
        for key, value in data.items():
            if key in self.fields:
                self.data['%s%s' % (prefix, key)] = value
        self.is_bound = True
    
    def to_json(self):
        return json.dumps(self.cleaned_data, cls=DjangoJSONEncoder)
    
    def as_full_table(self):
        if self.initial:
            key = self.initial.get('prototype', '')
        else:
            key = ''
        return u'<table class="%s">%s</table>' % (key, self.as_table())
    
    def as_widget(self):
        if self.initial:
            key = self.initial.get('prototype', '')
        else:
            key = ''
        info = dict()
        hidden = list()
        for name, field in self.fields.items():
            bf = BoundField(self, field, name)
            if bf.is_hidden:
                hidden.append(unicode(bf))
            else:
                info[name] = unicode(bf) #TODO include errors
        return u'<div class="%s">%s</div>' % (key, self.representation(info) + u''.join(hidden))
   
    def representation(self, info):
        return self.representation_string % info
        
class IfConditionForm(ConditionForm):
    representation_string = _(u'If %(concatenation)s are %(evaluation)s of the following:')

    concatenation = forms.ChoiceField(choices=[('ALL', _('ALL')), 
                                               ('ANY', _('ANY')),
                                               ('NONE', _('NONE'))])
    evaluation = forms.ChoiceField(choices=[('TRUE', _('TRUE')),
                                            ('FALSE', _('FALSE'))])
    
    subform_count = forms.IntegerField(initial=0, widget=forms.HiddenInput)
    subcondition = forms.ChoiceField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.subforms = list()
        super(IfConditionForm, self).__init__(*args, **kwargs)
        self.fields['subcondition'].choices = zip(self.language.operations.keys(), self.language.operations.keys())
    
    def make_subform_prefix(self, index):
        prefix = ''
        if self.prefix:
            prefix = '-' + self.prefix
        return str(index)+prefix
    
    def load_json(self, data):
        self._errors = None
        if isinstance(data, basestring):
            data = json.loads(data)
        super(IfConditionForm, self).load_json(data)
        self.subforms = list()
        for subform in data.get('conditions', []):
            if not subform:
                continue
            form = self.language.get(subform['prototype']).make_form(json=subform, prefix=self.make_subform_prefix(len(self.subforms)), auto_id=self.auto_id)
            self.subforms.append(form)
        self.data[self.add_prefix('subform_count')] = len(self.subforms)
        
    def clean(self):
        self.build_subforms()
        if not self.subforms:
            return {}
        self.cleaned_data['conditions'] = list()
        for form in self.subforms:
            if not form.is_valid():
                raise forms.ValidationError('Child logic is invalid')
            self.cleaned_data['conditions'].append(form.cleaned_data)
        self.cleaned_data.pop('subform_count', None)
        self.cleaned_data.pop('subcondition', None)
        return self.cleaned_data
        
    def build_subforms(self):
        '''
        Detects and builds subforms from self.data
        '''
        #self.subforms = list() #TODO we need to refactor so this doesn't break unit tests
        for i in range(int(self.data.get(self.add_prefix('subform_count'), 0))+1):
            key = '%s-prototype' % self.make_subform_prefix(i)
            if key in self.data:
                form = self.language.get(self.data[key]).make_form(data=self.data, prefix=self.make_subform_prefix(i), auto_id=self.auto_id)
                self.subforms.append(form)
    
    def as_widget(self):
        if self.initial:
            key = self.initial.get('prototype', '')
        else:
            key = ''
        conditions = super(IfConditionForm, self).as_widget()
        subconditions = list()
        for form in self.subforms:
            subconditions.append(u'<tr><td>%s</td><td><a class="deletelink" href="#">Remove</a></td></tr>' % form.as_widget())
        subconditions.append(u'<tr><td>Select subcondition: %s</td><td><a class="addlink" href="#">Add</a></td></tr>' % BoundField(self, self.fields['subcondition'], 'subcondition'))
        return u'<table class="hassubconditions %s"><tr><td>%s</td></tr><tr class="subconditions"><td><table>%s</table></td></tr></table>' % (key, conditions, u'\n'.join(subconditions))

class RuleField(forms.Field):
    #TODO refactor so the field has the form?
    def clean(self, value):
        '''
        Value gets piped from the widget, thus this form takes JSON
        '''
        value = super(RuleField, self).clean(value)
        if self.required and value == {}:
            raise forms.ValidationError(self.error_messages['required'])
        if isinstance(value, basestring) and value:
            value = json.loads(value)
        if value:
            form = self.widget.language.get(value['prototype']).make_form(json=value)
            if not form.is_valid():
                raise forms.ValidationError('Child logic is invalid')
        return value
        
