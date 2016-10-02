import json
from math import sqrt

import numpy as np
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri
from scipy import stats
from sqlalchemy import TypeDecorator, VARCHAR


class ArimaModel(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.
    """

    impl = VARCHAR

    def __init__(self, *args, **kwargs):
        super(ArimaModel, self).__init__(*args, **kwargs)
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
        self.phi = None
        self.theta = None
        self._residuals_acf = None
        self._residuals_pacf = None
        self.residuals_acf = None
        self.residuals_pacf = None
        self.residuals_acf_clim = None
        self.residuals_pacf_clim = None
        self.data_acf = None
        self.data_pacf = None
        self.data_acf_clim = None
        self.data_pacf_clim = None

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
            model = ArimaModel()
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
        self._residuals_acf = ro.r('acf(fit$residuals, plot=FALSE, na.action=na.pass)')
        self._residuals_pacf = ro.r('pacf(fit$residuals, plot=FALSE, na.action=na.pass)')
        self._data_acf = ro.r('acf(x, plot=FALSE, na.action=na.pass)')
        self._data_pacf = ro.r('pacf(x, plot=FALSE, na.action=na.pass)')

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
            self.phi = list(self._model.rx2('model')[0])
            self.theta = list(self._model.rx2('model')[1])
            self.pred = list(self._predict.rx2('pred'))
            self.pred_se = list(self._predict.rx2('se'))
            self.residuals_acf = list(self._residuals_acf.rx2('acf'))
            self.residuals_acf_clim = stats.norm.ppf((1 + 0.95) / 2) / sqrt(self._residuals_acf.rx2('n.used')[0])
            self.residuals_pacf = list(self._residuals_pacf.rx2('acf'))
            self.residuals_pacf_clim = stats.norm.ppf((1 + 0.95) / 2) / sqrt(self._residuals_pacf.rx2('n.used')[0])
            self.data_acf = list(self._data_acf.rx2('acf'))
            self.data_acf_clim = stats.norm.ppf((1 + 0.95) / 2) / sqrt(self._data_acf.rx2('n.used')[0])
            self.data_pacf = list(self._data_pacf.rx2('acf'))
            self.data_pacf_clim = stats.norm.ppf((1 + 0.95) / 2) / sqrt(self._data_pacf.rx2('n.used')[0])

        return dict(p=self.p, d=self.d, q=self.q, P=self.P, D=self.D, Q=self.Q, m=self.m,
                    coef=self.coef, s_e=self.s_e, sigma2=self.sigma2, loglik=self.loglik, aic=self.aic,
                    residuals=self.residuals, phi=self.phi, theta=self.theta, pred=self.pred, pred_se=self.pred_se,
                    residuals_acf=self.residuals_acf, residuals_acf_clim=self.residuals_acf_clim,
                    residuals_pacf=self.residuals_pacf, residuals_pacf_clim=self.residuals_pacf_clim,
                    data_acf=self.data_acf, data_acf_clim=self.data_acf_clim,
                    data_pacf=self.data_pacf, data_pacf_clim=self.data_pacf_clim)
