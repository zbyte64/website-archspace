from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

from widgets import RuleSetWidget
from forms import RuleField

class JSONFieldBase(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    #__metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value
    
    def value_to_string(self, obj):
        value = getattr(obj, self.name, None)
        if isinstance(value, dict):
            return json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONFieldBase, self).value_to_string(obj)

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONFieldBase, self).get_db_prep_save(value)
    
    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        """
        # We'll just introspect ourselves, since we inherit.
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.TextField"
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)

class JSONField(JSONFieldBase):
    __metaclass__ = models.SubfieldBase #get max recursion if we don't do the base strategy

class RuleSetProxy(dict):
    def __init__(self, language, node):
        self.language = language
        super(RuleSetProxy, self).__init__(node)
    
    def evaluate(self, context, language=None):
        if not language:
            language = self.language
        return language.evaluate(context, self)

class RuleSetField(JSONFieldBase):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.language = kwargs.pop('language', None)
        super(RuleSetField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        ret = super(RuleSetField, self).to_python(value)
        if not isinstance(ret, dict):
            ret = dict()
        return RuleSetProxy(self.language, ret)
        return dict()
        return ret
    
    def formfield(self, **kwargs):
        defaults = dict(kwargs)
        defaults = {'form_class': RuleField}
        defaults['widget'] = RuleSetWidget(language=self.language) #TODO don't forcibly overide the widget being passed in
        return super(RuleSetField, self).formfield(**defaults)

