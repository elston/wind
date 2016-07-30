import json

import numpy as np
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri
from sqlalchemy import TypeDecorator, VARCHAR


class ArimaPriceModel(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def __init__(self, *args, **kwargs):
        super(ArimaPriceModel, self).__init__(*args, **kwargs)
        self.p = None
        self.d = None
        self.q = None
        self.P = None
        self.D = None
        self.Q = None
        self.m = None
        self._model = None
        self.coef = None
        self.s_e = None
        self.sigma2 = None
        self.aic = None
        self.loglik = None
        self.n_ahead = None
        self._predict = None
        self.pred = None
        self.pred_se = None
        self.residuals = None

    def set_parameters(self, p, d, q, P, D, Q, m, n_ahead=48):
        self.p = p
        self.d = d
        self.q = q
        self.P = P
        self.D = D
        self.Q = Q
        self.m = m
        self.n_ahead = n_ahead

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        else:
            return json.dumps(value.to_dict())

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        else:
            model = ArimaPriceModel()
            d = json.loads(value)
            for k, v in d.iteritems():
                setattr(model, k, v)
            return model

    def fit(self, values):
        ro.r.assign('x', numpy2ri.numpy2ri(values))
        ro.r('fit = arima(x=x, order=c(%d, %d, %d), seasonal = list(order = c(%d, %d, %d), period = %d))' %
             (self.p, self.d, self.q, self.P, self.D, self.Q, self.m))
        self._model = ro.r('fit')
        self._predict = ro.r('predict(fit, n.ahead=%d)' % self.n_ahead)

    def to_dict(self):
        if self._model is not None:
            coef = self._model.rx2('coef')
            self.coef = dict(zip(coef.names, list(coef)))
            var_coef = np.array(self._model.rx2('var.coef'))
            s_e_coef = np.sqrt(np.diag(var_coef))
            s_e_coef = [x if np.isfinite(x) else None for x in s_e_coef]
            self.s_e = dict(zip(coef.names, s_e_coef))
            self.sigma2 = self._model.rx2('sigma2')[0]
            self.aic = self._model.rx2('aic')[0]
            self.loglik = self._model.rx2('loglik')[0]
            self.residuals = list(self._model.rx2('residuals'))
            self.pred = list(self._predict.rx2('pred'))
            self.pred_se = list(self._predict.rx2('se'))

        return dict(p=self.p, d=self.d, q=self.q, P=self.P, D=self.D, Q=self.Q, m=self.m,
                    coef=self.coef, s_e=self.s_e, sigma2=self.sigma2, loglik=self.loglik, aic=self.aic,
                    residuals=self.residuals, pred=self.pred, pred_se=self.pred_se)

        # def to_json(self):
        #     return json.dumps(self.to_dict())


'''
class PriceModel(object):
    class Model(object):
        @property
        def data(self):
            return self._data

        @property
        def model(self):
            return self._modelel

        @property
        def description(self):
            return self._description

        @property
        def prediction(self):
            return self._prediction

        def __init__(self, data=None, model=None, description=None):
            self._data = data
            self._model = model
            self._description = description
            self._prediction = None

        def __str__(self):
            return str(self._model)

        def as_dict(self):
            coef = self._model.rx2('coef')
            coef_d = dict(zip(coef.names, list(coef)))
            var_coef = np.array(self._model.rx2('var.coef'))
            s_e_coef = np.sqrt(np.diag(var_coef))
            s_e_coef_d = dict(zip(coef.names, s_e_coef))
            sigma2 = self._model.rx2('sigma2')[0]
            aic = self._model.rx2('aic')[0]
            loglik = self._model.rx2('loglik')[0]

            return {'coef': coef_d, 's.e': s_e_coef_d, 'sigma2': sigma2, 'loglik': loglik, 'aic': aic}

        def __repr__(self):
            return json.dumps(self.as_dict())

        def predict(self, n_ahead):
            ro.r.assign('model', self._model)
            ro.r.assign('n.ahead', n_ahead)
            res = ro.r('predict(model, n.ahead=n.ahead)')

            pred = res.rx2('pred')
            se = res.rx2('se')
            last_date = self._data.index[-1]

            def perdelta(start, end, delta):
                curr = start
                while curr < end:
                    yield curr
                    curr += delta

            pred_dates = perdelta(last_date + timedelta(hours=1),
                                  last_date + timedelta(hours=n_ahead + 1),
                                  timedelta(hours=1))
            self._prediction = pd.DataFrame(index=pred_dates, data={'pred': pred, 'se': se})
            return self._prediction

    def __init__(self):
        self.data = None
        self.lambdaD_model = None
        self.MAvsMD_model = None
        self.imbalance_model = None

    def fit_models(self):
        self.fit_lambdaD()
        self.fit_MAvsMD()
        self.fit_imbalance()

    def fit_lambdaD(self):
        data = np.log(self.data['lambdaD'])
        ro.r.assign('x', pandas2ri.py2ri(data))
        ro.r('fit = arima(x=x, order=c(2,0,1), seasonal = list(order = c(1, 1, 1), period = 24))')
        self.lambdaD_model = PriceModel.Model(data=data, model=ro.r('fit'), description='ARIMA(2,0,1)(1,1,1)24')
        # ro.r('fit = arima(x=x, order=c(5,1,1))')
        print(self.lambdaD_model)

    def fit_MAvsMD(self):
        data = self.data['MAvsMD']
        ro.r.assign('x', pandas2ri.py2ri(data))
        ro.r('fit = arima(x=x, order=c(1,0,11), seasonal = list(order = c(1, 0, 1), period = 24))')
        self.MAvsMD_model = PriceModel.Model(data=data, model=ro.r('fit'), description='ARIMA(1,0,11)(1,0,1)24')
        # ro.r('fit = arima(x=x, order=c(3,0,1))')
        # self.MAvsMD_model = PriceModel.Model(data=data, model=ro.r('fit'), description='ARIMA(3,0,1)')
        print(self.MAvsMD_model)

    def fit_imbalance(self):
        data = self.data['imbalance']
        ro.r.assign('x', pandas2ri.py2ri(data))
        ro.r('fit = arima(x=x, order=c(2,0,1), seasonal = list(order = c(1, 0, 1), period = 24))')
        self.imbalance_model = PriceModel.Model(data=data, model=ro.r('fit'), description='ARIMA(2,0,1)(1,0,1)24')
        # ro.r('fit = arima(x=x, order=c(4,0,5))')
        # self.imbalance_model = PriceModel.Model(data=data, model=ro.r('fit'), description='ARIMA(4,0,5)')
        print(self.imbalance_model)'''
