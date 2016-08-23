import json
import flask

from sqlalchemy import TypeDecorator, VARCHAR


class OptimizationResults(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def __init__(self, *args, **kwargs):
        super(OptimizationResults, self).__init__(*args, **kwargs)
        self.computing_start = None
        self.computing_finish = None
        self.expected_profit = None
        self.profit_std = None
        self.cvar = None
        self.Pd = None
        self.Pa = None
        self.Ps = None

    def set_parameters(self):
        pass

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return flask.json.dumps(value.to_dict())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            model = OptimizationResults()
            d = json.loads(value)
            for k, v in d.iteritems():
                setattr(model, k, v)
            return model

    def to_dict(self):
        return dict(computing_start=self.computing_start, computing_finish=self.computing_finish,
                    expected_profit=self.expected_profit, profit_std=self.profit_std, cvar=self.cvar,
                    Pd=self.Pd, Pa=self.Pa, Ps=self.Ps)
