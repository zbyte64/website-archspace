from forms import IfConditionForm

class Language(object):
    def __init__(self):
        self.operations = dict()
    
    def get(self, key):
        return self.operations[key](self, key)
    
    def add(self, key, condition):
        self.operations[key] = condition
    
    def evaluate(self, context, node):
        if not node:
            return True
        condition = self.get(node['prototype'])
        return condition.evaluate(context, node)

class Condition(object):
    form = None

    def __init__(self, language, key):
        self.language = language
        self.key = key
    
    def evaluate(self, context, node):
        raise NotImplementedError
    
    def make_form(self, *args, **kwargs):
        kwargs['key'] = self.key
        kwargs['language'] = self.language
        return self.form(*args, **kwargs)

class IfCondition(Condition):
    """
    NONE + TRUE => ALL + FALSE
    NONE + FALSE => ALL + TRUE
    """
    form = IfConditionForm
    
    def evaluate(self, context, node):
        if not len(node['conditions']): #Empty conditions always evaluate to true
            return True
        concat = node['concatenation']
        evaluation = node['evaluation']
        if concat == 'NONE':
            concat = 'ALL'
            if 'TRUE' == evaluation:
                evaluation = 'FALSE'
            else:
                evaluation = 'TRUE'
        if concat == 'ANY':
            for result in self._iterate(context, node):
                if str(result).upper() == evaluation:
                    return True
            return False
        assert concat == 'ALL'
        for result in self._iterate(context, node):
            if str(result).upper() != evaluation:
                return False
        return True
                
    def _iterate(self, context, node):
        for subcondition in node['conditions']:
            try:
                condition = self.language.get(subcondition['prototype'])
            except KeyError:
                pass
            else:
                yield condition.evaluate(context, subcondition)

