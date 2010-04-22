from django.test import TestCase
from django.utils import simplejson
from django import forms

from conditions import *
from forms import *

class IntComparisonForm(ConditionForm):
    representation_string = u'%(arg1)s is %(operator)s %(arg2)s'
    arg1 = forms.IntegerField()
    operator = forms.ChoiceField(choices=[('eq','equal to'),
                                          ('gt','greater then'),
                                          ('lt','less then')])
    arg2 = forms.IntegerField()

class IntComparisonCondition(Condition):
    form = IntComparisonForm

    operations = {'eq': lambda x, y: x == y,
                  'gt': lambda x, y: x > y,
                  'lt': lambda x, y: x < y}

    def evaluate(self, context, node):
        arg1 = int(node['arg1'])
        arg2 = int(node['arg2'])
        return self.operations[node['operator']](arg1, arg2)

BASIC_LANGUAGE = Language()
BASIC_LANGUAGE.add('if', IfCondition)
BASIC_LANGUAGE.add('intcompare', IntComparisonCondition)

from django.db import models
from fields import RuleSetField

class TestRules(models.Model):
    rules = RuleSetField(language=BASIC_LANGUAGE)

class TestRulesForm(forms.ModelForm):
    anotherfield = forms.CharField()

    class Meta:
        model = TestRules

class RuleBuilderTest(TestCase):
    def build_language(self):
        return BASIC_LANGUAGE
    
    def test_language_construct(self):
        language = self.build_language()
        self.assertTrue(language.evaluate(None, 
                                         {'prototype':'intcompare',
                                          'arg1':1,
                                          'arg2':2,
                                          'operator':'lt'}))
        self.assertFalse(language.evaluate(None, 
                                         {'prototype':'intcompare',
                                          'arg1':1,
                                          'arg2':2,
                                          'operator':'gt'}))
    
    def test_if_comparison(self):
        language = self.build_language()
        self.assertTrue(language.evaluate(None, 
                                        {'prototype':'if',
                                         'concatenation':'ALL',
                                         'evaluation':'TRUE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'}]
                                         }))
        self.assertFalse(language.evaluate(None, 
                                        {'prototype':'if',
                                         'concatenation':'ALL',
                                         'evaluation':'TRUE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                                         }))
        self.assertTrue(language.evaluate(None, 
                                        {'prototype':'if',
                                         'concatenation':'ANY',
                                         'evaluation':'TRUE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                                         }))
        self.assertFalse(language.evaluate(None, 
                                        {'prototype':'if',
                                         'concatenation':'NONE',
                                         'evaluation':'FALSE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                                         }))
    
    def test_field_errors(self):
        language = self.build_language()
        bad_data =  {'rules-prototype':'if',
                     'rules-concatenation':'ALL',
                     'rules-evaluation':'TRUE',
                     'rules-subform_count':1,
                     '0-rules-prototype':'intcompare',
                     #'0-rules-arg1':1,
                     #'0-rules-arg2':2,
                     '0-rules-operator':'lt',
                     '1-rules-prototype':'intcompare',
                     '1-rules-arg1':5,
                     '1-rules-arg2':2,
                     '1-rules-operator':'gt'
                     }
        submitted_form = language.get('if').make_form(data=bad_data, prefix='rules')
        self.assertFalse(submitted_form.is_valid(), submitted_form.errors)
        submitted_form.as_widget()
        self.assertEqual(2, len(submitted_form.subforms), 'Subforms were not preserved')
        rule_widget = TestRules._meta.get_field('rules').formfield().widget
        rule_value_json = rule_widget.value_from_datadict(bad_data, None, 'rules')
        self.assertFalse(rule_value_json)
        #print rule_value_json
        #print rule_widget.render('rules', rule_value_json)
        self.assertFalse('name="rules-subform_count" value="0"' in rule_widget.render('rules', rule_value_json))
        form_field = TestRules._meta.get_field('rules').formfield()
        bad_data_no_prefix =  {'prototype':'if',
                                         'concatenation':'NONE',
                                         'evaluation':'FALSE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              #'arg1':1,
                                              #'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                              }
        self.assertRaises(forms.ValidationError, lambda: form_field.clean(bad_data_no_prefix))
        
        good_data_no_prefix =  {'prototype':'if',
                                         'concatenation':'NONE',
                                         'evaluation':'FALSE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                              }
        form_field.clean(good_data_no_prefix)
   
    def test_model_form(self):
        bad_data =  {'rules-prototype':'if',
                     'rules-concatenation':'ALL',
                     'rules-evaluation':'TRUE',
                     'rules-subform_count':2,
                     '0-rules-prototype':'intcompare',
                     #'0-rules-arg1':1,
                     #'0-rules-arg2':2,
                     '0-rules-operator':'lt',
                     '1-rules-prototype':'intcompare',
                     '1-rules-arg1':5,
                     '1-rules-arg2':2,
                     '1-rules-operator':'gt',
                     'foo':1,
                     'anotherfield':'foo',
                     }
        good_data =  {'rules-prototype':'if',
                     'rules-concatenation':'ALL',
                     'rules-evaluation':'TRUE',
                     'rules-subform_count':2,
                     '0-rules-prototype':'intcompare',
                     '0-rules-arg1':1,
                     '0-rules-arg2':2,
                     '0-rules-operator':'lt',
                     '1-rules-prototype':'intcompare',
                     '1-rules-arg1':5,
                     '1-rules-arg2':2,
                     '1-rules-operator':'gt',
                     'anotherfield':'foo',
                     }
        bad_form = TestRulesForm(data=bad_data)
        self.assertTrue(bad_form.changed_data, bad_form.changed_data)
        self.assertFalse(bad_form.is_valid())
        self.assertFalse('name="rules-subform_count" value="0"' in bad_form.as_table())
        self.assertTrue('<input type="hidden" name="rules-subform_count" value="2" />' in bad_form.as_table())
        self.assertFalse('<input type="hidden" name="rules-prototype" />' in bad_form.as_table(), 'We lost our prototype')
        good_form = TestRulesForm(data=good_data)
        self.assertTrue(good_form.is_valid(), good_form.errors)
        self.assertTrue('<input type="hidden" name="rules-subform_count" value="2" />' in good_form.as_table())
        good_form.save()
        
        missing_data =  {'rules-prototype':'if',
                     'rules-concatenation':'ALL',
                     'rules-evaluation':'TRUE',
                     'rules-subform_count':2,
                     '0-rules-prototype':'intcompare',
                     '0-rules-arg1':1,
                     '0-rules-arg2':2,
                     '0-rules-operator':'lt',
                     '1-rules-prototype':'intcompare',
                     '1-rules-arg1':5,
                     '1-rules-arg2':2,
                     '1-rules-operator':'gt',
                     #'anotherfield':'foo',
                     }
        bad_form = TestRulesForm(data=missing_data)
        self.assertFalse(bad_form.is_valid())
        self.assertTrue('<input type="hidden" name="rules-subform_count" value="2" />' in bad_form.as_table())
    
    def test_model_form_properly_detects_if_changed(self):
        empty_data = {'rules-prototype':'if',
                      'rules-concatenation':'ALL',
                      'rules-evaluation':'TRUE',
                      'rules-subform_count':2,}
        empty_form = TestRulesForm(data=empty_data)
        self.assertFalse(empty_form.changed_data, empty_form.changed_data)
        
    def test_base_form(self):
        language = self.build_language()
        initial_form = language.get('intcompare').make_form()
        submitted_form = language.get('intcompare').make_form(data={'arg1':'1', 'arg2':'2', 'operator':'lt', 'prototype':'intcompare'})
        self.assertTrue(submitted_form.is_valid(), submitted_form.errors)
        loaded_json = submitted_form.to_json()
        initial_form.load_json(loaded_json)
        self.assertTrue(initial_form.is_valid(), initial_form.errors)
        self.assertTrue(language.evaluate(None, initial_form.cleaned_data))
        
    def test_if_form(self):
        language = self.build_language()
        initial_form = language.get('if').make_form()
        language.get('if').make_form(json={'prototype':'if',
                                         'concatenation':'ALL',
                                         'evaluation':'TRUE',})
        submitted_form = language.get('if').make_form(data={'prototype':'if',
                                         'concatenation':'ALL',
                                         'evaluation':'TRUE',
                                         'subform_count':1,
                                         '0-prototype':'intcompare',
                                         '0-arg1':1,
                                         '0-arg2':2,
                                         '0-operator':'lt',
                                         '1-prototype':'intcompare',
                                         '1-arg1':5,
                                         '1-arg2':2,
                                         '1-operator':'gt'
                                         })
        self.assertTrue(submitted_form.is_valid(), submitted_form.errors)
        loaded_json = submitted_form.to_json()
        initial_form.load_json(loaded_json)
        self.assertTrue(initial_form.is_valid(), initial_form.errors)
        self.assertTrue(language.evaluate(None, initial_form.cleaned_data))

    def test_rule_set_field(self):
        test_obj = TestRules(rules={'prototype':'if',
                                         'concatenation':'NONE',
                                         'evaluation':'FALSE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                                         })
        self.assertFalse(test_obj.rules.evaluate(None))
        test_obj.save()
        retrieved_obj = TestRules.objects.get(pk=test_obj.pk)
        self.assertFalse(retrieved_obj.rules.evaluate(None))
        
    def test_rule_set_widget(self):
        sample_rules = {'prototype':'if',
                                         'concatenation':'NONE',
                                         'evaluation':'FALSE',
                                         'conditions':[
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'lt'},
                                             {'prototype':'intcompare',
                                              'arg1':1,
                                              'arg2':2,
                                              'operator':'gt'}
                                         ]
                                         }
        test_obj = TestRules(rules=sample_rules)
        test_obj._meta.get_field('rules').formfield().widget.render('rules', None)
        test_obj._meta.get_field('rules').formfield().widget.render('rules', test_obj.rules)
        test_obj._meta.get_field('rules').formfield().widget.value_from_datadict(sample_rules, None, '')

