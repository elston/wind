from datetime import datetime
import logging

import numpy as np
from webapp import db
from webapp.api.math.reduce_scenarios import reduce_scenarios
from webapp.api.math.wind_producer_opt import Input, Optimizator
from webapp.models import Windpark
from webapp.models.optimization_job import OptimizationJob
from webapp.models.optimization_results import OptimizationResults

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Optimizer(object):
    def __init__(self, windpark_id, log_handler=None):
        if log_handler is not None:
            logging.getLogger().addHandler(log_handler)
        self.result = OptimizationResults()
        self.windpark = db.session.query(Windpark).filter_by(id=windpark_id).first()

    def optimize(self, job=OptimizationJob()):
        self.start()
        if job.refit_weather:
            self.start_refit_weather()
            self.windpark.location.fit_get_wspd_model()
            self.finish_refit_weather()
        if job.refit_market:
            self.start_refit_market()
            self.windpark.market.fit_price_model()
            self.finish_refit_market()

        self.start_scenarios_generation()
        _, PD = self.windpark.simulate_generation(time_span=job.time_span, n_samples=job.n_wind_scenarios)
        PD_red, PD_prob = reduce_scenarios(PD, np.ones(job.n_wind_scenarios) / job.n_wind_scenarios,
                                           job.n_redc_wind_scenarios)

        lambdaD, MAvsMD, sqrt_r = self.windpark.simulate_market(date=job.date, time_span=job.time_span,
                                                                n_samples=job.n_wind_scenarios)  # TODO: wrong. we need separate n
        lambdaD_red, lambdaD_prob = reduce_scenarios(lambdaD,
                                                     np.ones(job.n_lambdaD_scenarios) / job.n_lambdaD_scenarios,
                                                     job.n_redc_lambdaD_scenarios)
        MAvsMD_red, MAvsMD_prob = reduce_scenarios(MAvsMD, np.ones(job.n_MAvsMD_scenarios) / job.n_MAvsMD_scenarios,
                                                   job.n_redc_MAvsMD_scenarios)
        sqrt_r_red, sqrt_r_prob = reduce_scenarios(sqrt_r, np.ones(job.n_sqrt_r_scenarios) / job.n_sqrt_r_scenarios,
                                                   job.n_redc_sqrt_r_scenarios)

        D = job.n_redc_lambdaD_scenarios
        L = 1  # do not use 2-stage wind simulation (chapter 6.4.2) (temporarily)
        A = job.n_redc_MAvsMD_scenarios
        W = job.n_redc_wind_scenarios
        K = job.n_redc_sqrt_r_scenarios
        NT = job.time_span

        pi = np.empty((D, L, A, W, K))
        for d in xrange(D):
            for l in xrange(L):
                for a in xrange(A):
                    for w in xrange(W):
                        for k in xrange(K):
                            pi[d, l, a, w, k] = lambdaD_prob[d] * 1 * MAvsMD_prob[a] * PD_prob[w] * sqrt_r_prob[k]
        r = np.power(sqrt_r_red, 2)
        r_pos = np.minimum(r, 1)
        r_neg = np.maximum(r, 1)

        inp = Input(D=D, L=L, A=A, W=W, K=K, NT=NT,
                    dt=job.dt,
                    Pmax=job.Pmax,
                    alfa=job.alpha,
                    beta=job.beta,
                    P=PD_red.reshape(1, W, NT),
                    lambdaD=lambdaD_red,
                    MAvsMD=MAvsMD_red,
                    r_pos=r_pos,
                    r_neg=r_neg,
                    pi=pi
                    )

        n_variables = D * NT * (1 + 2 * L * (1 + W)) + 1 + D * L * A * W * K
        n_constraints = D * (L * A * W * K + NT * (5 * L * W + 3 * L + 2 * D + L * A * W * K))

        self.start_optimization(n_variables, n_constraints)
        opt_result = Optimizator()(inp)
        self.finish()

        self.result.expected_profit = opt_result.expected_profit()
        self.result.profit_std = opt_result.profit_std()
        self.result.cvar = opt_result.cvar()
        self.result.Pd = opt_result.variables.Pd.tolist()
        self.result.Pa = opt_result.variables.Pa.tolist()
        self.result.Ps = opt_result.variables.Ps.tolist()
        return self.result

    def start(self):
        logging.info('Starting optimization for wind park %s', self.windpark.name)
        self.result.computing_start = datetime.now()

    def finish(self):
        logging.info('Finished optimization for wind park %s', self.windpark.name)
        self.result.computing_finish = datetime.now()

    def start_refit_weather(self):
        logging.info('Starting fitting wind model for location %s', self.windpark.location.name)

    def finish_refit_weather(self):
        logging.info('Finished fitting wind model')

    def start_refit_market(self):
        logging.info('Starting fitting market model for market %s', self.windpark.market.name)

    def finish_refit_market(self):
        logging.info('Finished fitting market model')

    def start_scenarios_generation(self):
        logging.info('Starting scenarios generation for windpark %s', self.windpark.name)

    def start_optimization(self, n_variables, n_constraints):
        logging.info('Starting LP solving for windpark %s with %d variables, %d constraints', self.windpark.name,
                     n_variables, n_constraints)
