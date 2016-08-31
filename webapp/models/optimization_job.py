import csv
from datetime import date, datetime
import json
import cStringIO

from sqlalchemy import TypeDecorator, VARCHAR


class OptimizationJob(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def __init__(self, *args, **kwargs):
        super(OptimizationJob, self).__init__(*args, **kwargs)
        self.refit_weather = False
        self.refit_market = False
        self.n_da_am_wind_scenarios = 10
        self.n_redc_da_am_wind_scenarios = 3
        self.n_wind_scenarios = 10
        self.n_redc_wind_scenarios = 3
        self.n_lambdaD_scenarios = 100
        self.n_redc_lambdaD_scenarios = 4
        self.n_MAvsMD_scenarios = 100
        self.n_redc_MAvsMD_scenarios = 4
        self.n_sqrt_r_scenarios = 100
        self.n_redc_sqrt_r_scenarios = 4
        self.market_start_hour = 22
        self.time_span = 24
        self.date = date.today()
        self.dt = 1.0
        self.Pmax = 1.0
        self.alpha = 0.95
        self.beta = 0

    def set_parameters(self):
        pass

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return json.dumps(value.to_dict())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            model = OptimizationJob()
            d = json.loads(value)
            for k, v in d.iteritems():
                if k == 'date':
                    try:
                        setattr(model, k, datetime.strptime(v, '%Y-%m-%d').date())
                    except:
                        pass
                else:
                    setattr(model, k, v)
            return model

    def to_dict(self):
        return dict(refit_weather=self.refit_weather, refit_market=self.refit_market,
                    n_wind_scenarios=self.n_wind_scenarios, n_redc_wind_scenarios=self.n_redc_wind_scenarios,
                    n_da_am_wind_scenarios=self.n_da_am_wind_scenarios,
                    n_redc_da_am_wind_scenarios=self.n_redc_da_am_wind_scenarios,
                    n_lambdaD_scenarios=self.n_lambdaD_scenarios,
                    n_redc_lambdaD_scenarios=self.n_redc_lambdaD_scenarios,
                    n_MAvsMD_scenarios=self.n_MAvsMD_scenarios, n_redc_MAvsMD_scenarios=self.n_redc_MAvsMD_scenarios,
                    n_sqrt_r_scenarios=self.n_sqrt_r_scenarios, n_redc_sqrt_r_scenarios=self.n_redc_sqrt_r_scenarios,
                    market_start_hour=self.market_start_hour, time_span=self.time_span, date=self.date.isoformat(),
                    dt=self.dt,
                    Pmax=self.Pmax, alpha=self.alpha, beta=self.beta)

    def get_csv(self):
        fields = ['name', 'value']
        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        writer.writerow(('refit_weather', self.refit_weather))
        writer.writerow(('refit_market', self.refit_market))
        writer.writerow(('n_wind_scenarios', self.n_wind_scenarios))
        writer.writerow(('n_redc_wind_scenarios', self.n_redc_wind_scenarios))
        writer.writerow(('n_da_am_wind_scenarios', self.n_da_am_wind_scenarios))
        writer.writerow(('n_redc_da_am_wind_scenarios', self.n_redc_da_am_wind_scenarios))
        writer.writerow(('n_lambdaD_scenarios', self.n_lambdaD_scenarios))
        writer.writerow(('n_redc_lambdaD_scenarios', self.n_redc_lambdaD_scenarios))
        writer.writerow(('n_MAvsMD_scenarios', self.n_MAvsMD_scenarios))
        writer.writerow(('n_redc_MAvsMD_scenarios', self.n_redc_MAvsMD_scenarios))
        writer.writerow(('n_sqrt_r_scenarios', self.n_sqrt_r_scenarios))
        writer.writerow(('n_redc_sqrt_r_scenarios', self.n_redc_sqrt_r_scenarios))
        writer.writerow(('market_start_hour', self.market_start_hour))
        writer.writerow(('time_span', self.time_span))
        writer.writerow(('date', self.date.isoformat()))
        writer.writerow(('dt', self.dt))
        writer.writerow(('Pmax', self.Pmax))
        writer.writerow(('alpha', self.alpha))
        writer.writerow(('beta', self.beta))

        return csv_file.getvalue()
