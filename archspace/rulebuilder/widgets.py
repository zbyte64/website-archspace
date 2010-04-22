from django.forms import widgets
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.forms.util import flatatt

def deserialize(value):
    if isinstance(value, basestring):
        try:
            return json.loads(value)
        except:
            return None #TODO: what should we do now?
    return value

class RuleSetWidget(widgets.Widget):
    '''
    Not a thread safe widget, instantiate for each use!
    '''
    class Media:
        js = ['/static/js/jquery.js', '/static/rulebuilder/js/builder.js']
    
    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language')
        self.base_form = None
        self.form_defs = dict()
        super(RuleSetWidget, self).__init__(*args, **kwargs)

    def _update_form_defs(self, language, key):
        operation = language.get(key)
        self.form_defs.setdefault(key, operation.make_form(auto_id=False, prefix='_proto').as_widget())

    def init_form_defs(self):
        self.form_defs = dict()
        #TODO make more DRY
        for key in self.language.operations.iterkeys():
            self._update_form_defs(self.language, key)
            operation = self.language.get(key)
            if operation.language != self.language:
                for skey in operation.language.operations.iterkeys():
                    self._update_form_defs(operation.language, skey)

    def load_json(self, name, node):
        node = deserialize(node)
        if self.base_form:
            if not node:
                return
            self.base_form.load_json(node)
        else:
            if node:
                self.base_form = self.language.get(node['prototype']).make_form(json=node, auto_id=False, prefix=name)
            else:
                self.base_form = self.language.get('if').make_form(auto_id=False, prefix=name)

    def render(self, name, node, attrs=None):
        '''
        Expects json
        '''
        self.load_json(name, node)
        if not attrs:
            attrs = {}
        if not self.form_defs:
            self.init_form_defs()
        attrs.update({'class': 'rulebuilder'})
        final_attrs = self.build_attrs(attrs)
        return mark_safe(u'<div%s><div class="available_prototypes" style="display:none">%s</div>%s</div>' % (flatatt(final_attrs), ''.join(self.form_defs.itervalues()), self.base_form.as_widget()))
    
    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        
        Expects POST type data, return JSON
        """
        prototype = data.get(name+"-prototype", None)
        if prototype:
            self.base_form = self.language.get(prototype).make_form(auto_id=False, prefix=name, data=data)
            if self.base_form.is_valid():
                return self.base_form.to_json()
        return data.get(name, {})
        
    def _has_changed(self, initial_value, data_value):
        initial_value = deserialize(initial_value)
        data_value = deserialize(data_value)
        if not initial_value and not data_value:
            return False
        return super(RuleSetWidget, self)._has_changed(initial_value, data_value)
        
