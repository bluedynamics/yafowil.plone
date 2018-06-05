class YafowilAutoformPersistWriter(object):

    def __init__(self, field):
        self.field = field

    def __call__(self, model, target, value):
        if self.field.is_behavior:
            setattr(self.field.schema(model), target, value)
        else:
            setattr(model, target, value)
