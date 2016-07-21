#!/usr/bin/env python
import logging
from collections import OrderedDict, Iterable
from operator import itemgetter
import sys

import warnings
import numpy as np
from FuncDesigner import oovar
from openopt import MILP

warnings.simplefilter(action="ignore", category=FutureWarning)


# logging.basicConfig(filename='wind_producer_opt.log', level=logging.DEBUG)


class Input(tuple):
    """Input parameters for optimization"""

    __slots__ = ()  # prevents the creation of instance dictionaries

    _fields = (
        "D", "L", "A", "W", "K", "dt", "Pmax", "alfa", "beta", "P", "lambdaD", "MAvsMD", "r_pos", "r_neg", "pi", "NT")

    def __new__(_cls, D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi, NT):
        'Create new instance of Input(D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi, NT)'
        return tuple.__new__(_cls, (
            D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi, NT,))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'Input(D=%r, L=%r, A=%r, W=%r, K=%r, dt=%r, Pmax=%r, alfa=%r, beta=%r, P=%r, lambdaD=%r, MAvsMD=%r, r_pos=%r, r_neg=%r, pi=%r, NT=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    __dict__ = property(_asdict)

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    D = property(itemgetter(0), doc='Index for DA price scenarios, integer scalar')
    L = property(itemgetter(1), doc='Index for scenarios modeling wind production in between DA and AM, integer scalar')
    A = property(itemgetter(2), doc='Index for price differences between DA and AM, integer scalar')
    W = property(itemgetter(3), doc='Index for scenarios modeling wind production after AM, integer scalar')
    K = property(itemgetter(4), doc='Index for scenarios representing imbalance price ratios, integer scalar')
    dt = property(itemgetter(5), doc='Time span between two consecutive time periods (h), real scalar')
    Pmax = property(itemgetter(6), doc='Wind farm capacity (MW), real scalar')
    alfa = property(itemgetter(7), doc='Confidence level, real scalar')
    beta = property(itemgetter(8), doc='Risk-aversion parameter, real scalar')
    P = property(itemgetter(9),
                 doc='Wind power production, real LxW for s.p. LxWxNT for m.p.')  # s.p./m.p. = single/multi period
    lambdaD = property(itemgetter(10), doc='Day-ahead market prices, real D vec. for s.p. DxNT matr. for m.p.')
    MAvsMD = property(itemgetter(11),
                      doc='Price difference between day-ahead and adjustment markets, real A vec. for s.p. AxNT matr. for m.p.')
    r_pos = property(itemgetter(12),
                     doc='Imbalance price ratio for positive energy deviations, real K vec. for s.p. KxNT matr. for m.p.')
    r_neg = property(itemgetter(13),
                     doc='Imbalance price ratio for negative energy deviations, real K vec. for s.p. KxNT matr. for m.p.')
    pi = property(itemgetter(14), doc='Scenario probabilities, real DxLxAxWxK matrix')
    NT = property(itemgetter(15), doc='Index for time periods, integer scalar')


class Variables(tuple):
    'Variables(Pd, Pa, Ps, desvP, desvN, var, eta, )'

    __slots__ = ()  # prevents the creation of instance dictionaries

    _fields = ('Pd', 'Pa', 'Ps', 'desvP', 'desvN', 'var', 'eta')

    def __new__(_cls, Pd, Pa, Ps, desvP, desvN, var, eta):
        'Create new instance of Variables(Pd, Pa, Ps, desvP, desvN, var, eta)'
        return tuple.__new__(_cls, (Pd, Pa, Ps, desvP, desvN, var, eta))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'Variables(Pd=%r, Pa=%r, Ps=%r, desvP=%r, desvN=%r, var=%r, eta=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    __dict__ = property(_asdict)

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    Pd = property(itemgetter(0), doc='Power sold in the day-ahead market, real D vec for s.p., DxNT matr. for m.p.')
    Pa = property(itemgetter(1), doc='Power traded in the adjustment market, real DxL for s.p., DxLxNT for s.p.')
    Ps = property(itemgetter(2), doc='Final power schedule, real DxL for s.p., DxLxNT for m.p.')
    desvP = property(itemgetter(3), doc='Positive energy deviation, real DxLxW for s.p. DxLxWxNT for m.p.')
    desvN = property(itemgetter(4), doc='Negative energy deviation, real DxLxW for s.p. DxLxWxNT for m.p.')
    var = property(itemgetter(5), doc='Value-at-risk, real scalar')
    eta = property(itemgetter(6), doc='Auxiliary variable, real DxLxAxWxK metrix')


class Output(tuple):
    'Output(objective, variables, inp, internals)'

    __slots__ = ()  # prevents the creation of instance dictionaries

    _fields = ('objective', 'variables', 'inp', 'lambdaI', 'internals')

    def __new__(_cls, objective, variables, inp, lambdaI, internals):
        'Create new instance of Output(objective, variables, inp, lambdaI, internals)'
        return tuple.__new__(_cls, (objective, variables, inp, lambdaI, internals))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'Output(objective=%r, variables=%r, inp=%r, lambdaI=%r, internals=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    __dict__ = property(_asdict)

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    objective = property(itemgetter(0), doc='Value of objective function')
    variables = property(itemgetter(1), doc='Optimized variables')
    inp = property(itemgetter(2), doc='Input parameters')
    lambdaI = property(itemgetter(3), doc='Intermediate variable')
    internals = property(itemgetter(4), doc='Optimizer internal result')

    def profit_distribution(self):
        distribution = np.empty((self.inp.D, self.inp.L, self.inp.A, self.inp.W, self.inp.K))
        for d in xrange(self.inp.D):
            for l in xrange(self.inp.L):
                for a in xrange(self.inp.A):
                    for w in xrange(self.inp.W):
                        for k in xrange(self.inp.K):
                            profit = 0
                            for t in xrange(self.inp.NT):
                                profit += self.inp.dt * self.inp.lambdaD[d][t] * self.variables.Pd[d][t] \
                                          + self.inp.dt * self.lambdaI[d][a][t] * self.variables.Pa[d][l][t] \
                                          + self.inp.lambdaD[d][t] * self.inp.r_pos[k][t] * \
                                            self.variables.desvP[d][l][w][t] \
                                          - self.inp.lambdaD[d][t] * self.inp.r_neg[k][t] * \
                                            self.variables.desvN[d][l][w][t]
                            distribution[d][l][a][w][k] = profit

        return distribution

    def expected_profit(self):
        return np.sum(self.profit_distribution() * self.inp.pi)

    def profit_std(self):
        return np.sqrt(np.sum((self.profit_distribution() - self.expected_profit()) ** 2 * \
                              self.inp.pi))

    def cvar(self):
        return self.variables.var - \
               np.sum(self.inp.pi * self.variables.eta) / (1 - self.inp.alfa)

    def print_3d_array(self, data):
        print '# Array shape: {0}'.format(data.shape)
        for data_slice in data:
            np.savetxt(sys.stdout, data_slice, fmt='%-7.2f')
            print '# New slice'

    def print_output(self):
        print "beta: ", self.inp.beta
        print 'expected profit: %.2f' % self.expected_profit()
        print 'profit standard deviation: %.2f' % self.profit_std()
        print 'CVaR: %.2f' % self.cvar()
        print 'power sold in the day-ahead market'
        np.savetxt(sys.stdout, self.variables.Pd, fmt='%7.1f')
        print 'power traded in the adjustment market'
        self.print_3d_array(self.variables.Pa)
        print 'final power schedule'
        self.print_3d_array(self.variables.Ps)
        print 'initialization time: %.2fs, solver time: %.2fs' % \
              (self.internals.elapsed['initialization_time'], self.internals.elapsed['solver_time'])


class Optimizator():
    def __call__(self, *args, **kwargs):
        return self.optimize(args[0], **kwargs)

    @staticmethod
    def _flatten(lolol):
        """
        Flattens list of lists of lists with any depth
        :param lolol: list of lists of lists...
        """
        for elem in lolol:
            if isinstance(elem, Iterable) and not isinstance(elem, basestring):
                for sub in Optimizator._flatten(elem):
                    yield sub
            else:
                yield elem

    @staticmethod
    def check_dimensions(inp):
        assert inp.P.shape == (inp.L, inp.W, inp.NT)
        assert inp.lambdaD.shape == (inp.D, inp.NT)
        assert inp.MAvsMD.shape == (inp.A, inp.NT)
        assert inp.r_pos.shape == (inp.K, inp.NT)
        assert inp.r_neg.shape == (inp.K, inp.NT)
        assert inp.pi.shape == (inp.D, inp.L, inp.A, inp.W, inp.K)

    @staticmethod
    def optimize(inp, disable_am=False):
        Optimizator.check_dimensions(inp)

        lambdaI = inp.lambdaD.reshape(inp.D, 1, inp.NT) + inp.MAvsMD.reshape(1, inp.A, inp.NT)

        variables = Optimizator._make_variables(inp, disable_am)
        objective = Optimizator._make_objective(inp, variables, lambdaI)
        constraints = Optimizator._make_constraints(inp, variables, lambdaI)
        start_point = Optimizator._make_start_point(inp, variables)

        # free_vars = []
        # free_vars.extend(variables.eta)
        # free_vars.append(variables.var)
        problem = MILP(objective, start_point, constraints=constraints)
        result = problem.maximize('lpSolve', iprint=1)
        x = result.xf
        f = result.ff
        optimized_variables = Optimizator._parse_result(inp, variables, x)
        return Output(objective=f, variables=optimized_variables, inp=inp, lambdaI=lambdaI, internals=result)

    @staticmethod
    def _make_variables(inp, disable_am=False):

        Pd = []  # single period: Pd(D) Power sold in the day-ahead market
        # multi-perios Pd(D,NT)
        for d in xrange(inp.D):
            Pd.append([])
            for t in xrange(inp.NT):
                Pd[d].append(oovar("Pd(%d,%d)" % (d, t), lb=0, ub=inp.Pmax))

        Pa = []  # single period: Pa(D,L) Power traded in the adjustment market
        # multi period Pa(D,L,NT)
        for d in xrange(inp.D):
            Pa.append([])
            for l in xrange(inp.L):
                Pa[d].append([])
                for t in xrange(inp.NT):
                    if disable_am:
                        Pa[d][l].append(oovar("Pa(%d,%d,%d)" % (d, l, t), lb=0, ub=0))
                    else:
                        Pa[d][l].append(oovar("Pa(%d,%d,%d)" % (d, l, t)))

        Ps = []  # single period: Ps(D,L) Final power schedule
        # multi period: Ps(D,L,NT)
        for d in xrange(inp.D):
            Ps.append([])
            for l in xrange(inp.L):
                Ps[d].append([])
                for t in xrange(inp.NT):
                    Ps[d][l].append(oovar("Ps(%d,%d,%d)" % (d, l, t), lb=0, ub=inp.Pmax))

        desvP = []  # single period: desvP(D,L,W) Positive energy deviation
        # multi period desvP(D,L,W,NT)
        for d in xrange(inp.D):
            desvP.append([])
            for l in xrange(inp.L):
                desvP[d].append([])
                for w in xrange(inp.W):
                    desvP[d][l].append([])
                    for t in xrange(inp.NT):
                        desvP[d][l][w].append(oovar("desvP(%d,%d,%d,%d)" % (d, l, w, t), lb=0))

        desvN = []  # single period: desvN(D,L,W) Negative energy deviation
        # multi period desvN(D,L,W,NT)
        for d in xrange(inp.D):
            desvN.append([])
            for l in xrange(inp.L):
                desvN[d].append([])
                for w in xrange(inp.W):
                    desvN[d][l].append([])
                    for t in xrange(inp.NT):
                        desvN[d][l][w].append(oovar("desvN(%d,%d,%d,%d)" % (d, l, w, t), lb=0))

        var = oovar("var")  # Value-at-risk
        eta = []  # eta(D,L,A,W,K) Auxiliary variable
        for d in xrange(inp.D):
            eta.append([])
            for l in xrange(inp.L):
                eta[d].append([])
                for a in xrange(inp.A):
                    eta[d][l].append([])
                    for w in xrange(inp.W):
                        eta[d][l][a].append([])
                        for k in xrange(inp.K):
                            eta[d][l][a][w].append(oovar("eta(%d,%d,%d,%d,%d)" % (d, l, a, w, k), lb=0))

        return Variables(Pd=Pd, Pa=Pa, Ps=Ps, desvP=desvP, desvN=desvN, var=var, eta=eta)

    @staticmethod
    def _make_objective(inp, var, lambdaI):
        profit_exp = 0
        cvar_sum = 0
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            profit = 0
                            for t in xrange(inp.NT):
                                profit += inp.dt * inp.lambdaD[d][t] * var.Pd[d][t] \
                                          + inp.dt * lambdaI[d][a][t] * var.Pa[d][l][t] \
                                          + inp.lambdaD[d][t] * inp.r_pos[k][t] * var.desvP[d][l][w][t] \
                                          - inp.lambdaD[d][t] * inp.r_neg[k][t] * var.desvN[d][l][w][t]
                            profit_exp += inp.pi[d][l][a][w][k] * profit
                            cvar_sum += inp.pi[d][l][a][w][k] * var.eta[d][l][a][w][k]
        obj = profit_exp + inp.beta * (var.var - cvar_sum / (1 - inp.alfa))

        logging.debug("obj = %s", obj.expr)
        return obj

    @staticmethod
    def _make_constraints(inp, var, lambdaI):
        constraints = []

        # (6.53) defined in variable definition
        # (6.55) defined in variable definition

        # (6.56)+(6.57) devsP(d,l,w,t) - desvN(d,l,w,t) = dt * (P(l,w,t) - Ps(d,l,t))
        # old GAMS DesvDEF(D,L,W).. desvP(D,L,W)-desvN(D,L,W) =e= dt*(P(L,W) - Ps(D,L));
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        cons_part.append(var.desvP[d][l][w][t] - var.desvN[d][l][w][t] == inp.dt * (
                            inp.P[l][w][t] - var.Ps[d][l][t]))
        constraints.extend(cons_part)

        logging.debug("DesvDEF = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.58) desvP(d,l,w,t) <= P(l,w,t) * dt
        # old GAMS MAXdesvPOS(D,L,W).. desvP(D,L,W) =l= P(L,W)*dt;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        cons_part.append(var.desvP[d][l][w][t] <= inp.dt * inp.P[l][w][t])
        constraints.extend(cons_part)

        logging.debug("MAXdesvPOS = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.59) desvN(d,l,w,t) <= Pmax *dt
        # MAXdesvNEG(D,L,W).. desvN(D,L,W) =l= Pmax*dt;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        cons_part.append(var.desvN[d][l][w][t] <= inp.dt * inp.Pmax)
        constraints.extend(cons_part)

        logging.debug("MAXdesvNEG = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.54) Ps(d,l,t) = Pd(d,t) + Pa(d,l,t)
        # old GAMS PsDEF(D,L).. Ps(D,L) =e= Pd(D) + Pa(D,L);
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for t in xrange(inp.NT):
                    cons_part.append(var.Ps[d][l][t] == var.Pd[d][t] + var.Pa[d][l][t])
        constraints.extend(cons_part)

        logging.debug("PsDEF = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.60) Pd(d,t) - Pd(d',t) <= 0 if lambdaD(d',t) > lambdaD(d,t)
        # old GAMS curve(D,Daux)$(lambdaD(Daux) GT lambdaD(D)).. Pd(D)-Pd(Daux) =l= 0;
        cons_part = []
        for d in xrange(inp.D):
            for daux in xrange(inp.D):
                for t in xrange(inp.NT):
                    if d != daux and inp.lambdaD[daux][t] > inp.lambdaD[d][t]:
                        cons_part.append(var.Pd[d][t] - var.Pd[daux][t] <= 0)
        constraints.extend(cons_part)

        logging.debug("curve = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.61) Pd(d,t) = Pd(d',t) if lambdaD(d,t) = lambdaD(d',t)
        # old GAMS noANTICIPd(D,Daux)$(lambdaD(Daux) EQ lambdaD(D)).. Pd(D) =e= Pd(Daux);
        cons_part = []
        for d in xrange(inp.D):
            for daux in xrange(inp.D):
                for t in xrange(inp.NT):
                    if d != daux and inp.lambdaD[daux][t] == inp.lambdaD[d][t]:  # TODO: don't compare real numbers
                        cons_part.append(var.Pd[d][t] == var.Pd[daux][t])
        constraints.extend(cons_part)

        logging.debug("noANTICIPd = \n%s", "\n".join([x.expr for x in cons_part]))

        # (6.62) covered with darkness

        # (6.63) var - profit(d,l,a,w,k) - eta(d,l,a,w,k) < 0
        # old GAMS CVaRrest(D,L,A,W,K).. var - profit(D,L,A,W,K) - eta(D,L,A,W,K) =l= 0;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            profit = 0
                            for t in xrange(inp.NT):
                                profit += inp.dt * inp.lambdaD[d][t] * var.Pd[d][t] \
                                          + inp.dt * lambdaI[d][a][t] * var.Pa[d][l][t] \
                                          + inp.lambdaD[d][t] * inp.r_pos[k][t] * var.desvP[d][l][w][t] \
                                          - inp.lambdaD[d][t] * inp.r_neg[k][t] * var.desvN[d][l][w][t]
                            cons_part.append(var.var - profit - var.eta[d][l][a][w][k] < 0)
        constraints.extend(cons_part)

        logging.debug("CVaRrest = \n%s", "\n".join([x.expr for x in cons_part]))

        logging.debug("constraints = \n%s", "\n".join([x.expr for x in constraints]))
        return constraints

    @staticmethod
    def _make_start_point(inp, var):
        start_point = {}
        for d in xrange(inp.D):
            for t in xrange(inp.NT):
                start_point[var.Pd[d][t]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for t in xrange(inp.NT):
                    start_point[var.Pa[d][l][t]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for t in xrange(inp.NT):
                    start_point[var.Ps[d][l][t]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        start_point[var.desvP[d][l][w][t]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        start_point[var.desvN[d][l][w][t]] = 0

        start_point[var.var] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            start_point[var.eta[d][l][a][w][k]] = 0

        return start_point

    @staticmethod
    def _parse_result(inp, var, x):
        Pd = np.empty((inp.D, inp.NT))
        for d in xrange(inp.D):
            for t in xrange(inp.NT):
                Pd[d][t] = x[var.Pd[d][t]]

        Pa = np.empty((inp.D, inp.L, inp.NT))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for t in xrange(inp.NT):
                    Pa[d][l][t] = x[var.Pa[d][l][t]]

        Ps = np.empty((inp.D, inp.L, inp.NT))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for t in xrange(inp.NT):
                    Ps[d][l][t] = x[var.Ps[d][l][t]]

        desvP = np.empty((inp.D, inp.L, inp.W, inp.NT))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        desvP[d][l][w][t] = x[var.desvP[d][l][w][t]]

        desvN = np.empty((inp.D, inp.L, inp.W, inp.NT))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    for t in xrange(inp.NT):
                        desvN[d][l][w][t] = x[var.desvN[d][l][w][t]]

        xi = x[var.var]
        eta = np.empty((inp.D, inp.L, inp.A, inp.W, inp.K))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            eta[d][l][a][w][k] = x[var.eta[d][l][a][w][k]]

        return Variables(Pd=Pd, Pa=Pa, Ps=Ps, desvP=desvP, desvN=desvN, var=xi, eta=eta)
