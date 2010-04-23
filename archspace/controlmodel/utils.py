class MergeDict(dict):
    def update(self, other):
        for key, value in other.iteritems():
            if key in self:
                self[key] += value
            else:
                self[key] = value
