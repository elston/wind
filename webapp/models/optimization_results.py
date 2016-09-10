import csv
import json
import cStringIO

import flask
import numpy as np
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
        self.desvP = None
        self.desvN = None
        self.input = {}
        self.reduced_simulated_power = None
        self.power_probs = None

    def set_parameters(self):
        pass

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return flask.json.dumps(value.to_dict(detailed=True))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            model = OptimizationResults()
            d = json.loads(value)
            for k, v in d.iteritems():
                setattr(model, k, v)
            return model

    def to_dict(self, detailed=False):
        d = dict(computing_start=self.computing_start, computing_finish=self.computing_finish,
                 expected_profit=self.expected_profit, profit_std=self.profit_std, cvar=self.cvar,
                 Pd=self.Pd, Pa=self.Pa, Ps=self.Ps, desvP=self.desvP, desvN=self.desvN,
                 reduced_simulated_power=self.reduced_simulated_power, power_probs=self.power_probs)
        if detailed:
            d['input'] = self.input
        return d

    def get_general_csv(self):
        fields = ['name', 'value']
        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        writer.writerow(('computing_start', self.computing_start))
        writer.writerow(('computing_finish', self.computing_finish))
        writer.writerow(('expected_profit', self.expected_profit))
        writer.writerow(('profit_std', self.profit_std))
        writer.writerow(('cvar', self.cvar))

        return csv_file.getvalue()

    def get_generation_scenarios_csv(self):
        fields = ["l'", "w'"]
        fields.extend([str(i) for i in xrange(12, 24)])
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        generation_scenarios = np.array(self.input['simulated_power'])
        for l in xrange(generation_scenarios.shape[0]):
            for w in xrange(generation_scenarios.shape[1]):
                writer.writerow([l, w] + generation_scenarios[l, w, :].tolist())

        return csv_file.getvalue()

    def get_reduced_generation_scenarios_csv(self):
        fields = ["l'", "w'", 'p']
        fields.extend([str(i) for i in xrange(12, 24)])
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        generation_scenarios = np.array(self.input['reduced_simulated_power'])
        probs = np.array(self.input['simulated_power_probs'])
        for l in xrange(generation_scenarios.shape[0]):
            for w in xrange(generation_scenarios.shape[1]):
                writer.writerow([l, w, probs[l, w]] + generation_scenarios[l, w, :].tolist())

        return csv_file.getvalue()

    def get_da_price_scenarios_csv(self):
        fields = ['d']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        da_price_scenarios = np.array(self.input['lambdaD'])
        for d in xrange(da_price_scenarios.shape[0]):
            writer.writerow([d] + da_price_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_reduced_da_price_scenarios_csv(self):
        fields = ['d', 'p']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        da_price_scenarios = np.array(self.input['reduced_lambdaD'])
        probs = np.array(self.input['lambdaD_probs'])

        for d in xrange(da_price_scenarios.shape[0]):
            writer.writerow([d, probs[d]] + da_price_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_da_am_diff_scenarios_csv(self):
        fields = ['a']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        da_am_diff_scenarios = np.array(self.input['MAvsMD'])
        for d in xrange(da_am_diff_scenarios.shape[0]):
            writer.writerow([d] + da_am_diff_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_reduced_da_am_diff_scenarios_csv(self):
        fields = ['a', 'p']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        da_am_diff_scenarios = np.array(self.input['reduced_MAvsMD'])
        probs = np.array(self.input['MAvsMD_probs'])

        for d in xrange(da_am_diff_scenarios.shape[0]):
            writer.writerow([d, probs[d]] + da_am_diff_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_imbalance_scenarios_csv(self):
        fields = ['a']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        imbalance_scenarios = np.array(self.input['sqrt_r'])
        for d in xrange(imbalance_scenarios.shape[0]):
            writer.writerow([d] + imbalance_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_reduced_imbalance_scenarios_csv(self):
        fields = ['a', 'p']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        imbalance_scenarios = np.array(self.input['reduced_sqrt_r'])
        probs = np.array(self.input['sqrt_r_probs'])

        for d in xrange(imbalance_scenarios.shape[0]):
            writer.writerow([d, probs[d]] + imbalance_scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_da_volumes_csv(self):
        fields = ['d']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        scenarios = np.array(self.Pd)
        for d in xrange(scenarios.shape[0]):
            writer.writerow([d] + scenarios[d, :].tolist())

        return csv_file.getvalue()

    def get_am_volumes_csv(self):
        fields = ['d', 'l']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        scenarios = np.array(self.Pa)
        for d in xrange(scenarios.shape[0]):
            for l in xrange(scenarios.shape[1]):
                writer.writerow([d, l] + scenarios[d, l, :].tolist())

        return csv_file.getvalue()

    def get_total_volumes_csv(self):
        fields = ['d', 'l']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        scenarios = np.array(self.Ps)
        for d in xrange(scenarios.shape[0]):
            for l in xrange(scenarios.shape[1]):
                writer.writerow([d, l] + scenarios[d, l, :].tolist())

        return csv_file.getvalue()

    def get_positive_deviations_csv(self):
        fields = ['d', 'l', 'w']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        scenarios = np.array(self.desvP)
        for d in xrange(scenarios.shape[0]):
            for l in xrange(scenarios.shape[1]):
                for w in xrange(scenarios.shape[2]):
                    writer.writerow([d, l, w] + scenarios[d, l, w, :].tolist())

        return csv_file.getvalue()

    def get_negative_deviations_csv(self):
        fields = ['d', 'l', 'w']
        fields.extend([str(i) for i in xrange(24)])

        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        scenarios = np.array(self.desvN)
        for d in xrange(scenarios.shape[0]):
            for l in xrange(scenarios.shape[1]):
                for w in xrange(scenarios.shape[2]):
                    writer.writerow([d, l, w] + scenarios[d, l, w, :].tolist())

        return csv_file.getvalue()
