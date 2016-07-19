#!/usr/bin/env python
import logging
import warnings
from collections import OrderedDict, Iterable
from operator import itemgetter
import sys

import numpy as np
from FuncDesigner import oovar
from openopt import MILP


warnings.simplefilter(action="ignore", category=FutureWarning)
# logging.basicConfig(filename='wind_producer_opt.log', level=logging.DEBUG)


class Input(tuple):
    """Input parameters for optimization"""

    __slots__ = ()  # prevents the creation of instance dictionaries

    _fields = (
        "D", "L", "A", "W", "K", "dt", "Pmax", "alfa", "beta", "P", "lambdaD", "MAvsMD", "r_pos", "r_neg", "pi", )

    def __new__(_cls, D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi):
        'Create new instance of Input(D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi)'
        return tuple.__new__(_cls, (
            D, L, A, W, K, dt, Pmax, alfa, beta, P, lambdaD, MAvsMD, r_pos, r_neg, pi, ))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return 'Input(D=%r, L=%r, A=%r, W=%r, K=%r, dt=%r, Pmax=%r, alfa=%r, beta=%r, P=%r, lambdaD=%r, MAvsMD=%r, r_pos=%r, r_neg=%r, pi=%r)' % self

    def _asdict(self):
        'Return a new OrderedDict which maps field names to their values'
        return OrderedDict(zip(self._fields, self))

    __dict__ = property(_asdict)

    def __getnewargs__(self):
        'Return self as a plain tuple.  Used by copy and pickle.'
        return tuple(self)

    D = property(itemgetter(0), doc='Index for DA price scenarios')
    L = property(itemgetter(1), doc='Index for price differences between DA and AM')
    A = property(itemgetter(2), doc='Index for scenarios modeling wind production in between DA and AM')
    W = property(itemgetter(3), doc='Index for scenarios modeling wind production after AM')
    K = property(itemgetter(4), doc='Index for scenarios representing imbalance price ratios')
    dt = property(itemgetter(5), doc='Time span between two consecutive time periods (h)')
    Pmax = property(itemgetter(6), doc='Wind farm capacity (MW)')
    alfa = property(itemgetter(7), doc='Confidence level ')
    beta = property(itemgetter(8), doc='Risk-aversion parameter')
    P = property(itemgetter(9), doc='Wind power production')
    lambdaD = property(itemgetter(10), doc='Day-ahead market prices')
    MAvsMD = property(itemgetter(11), doc='Price difference between day-ahead and adjustment markets')
    r_pos = property(itemgetter(12), doc='Imbalance price ratio for positive energy deviations')
    r_neg = property(itemgetter(13), doc='Imbalance price ratio for negative energy deviations')
    pi = property(itemgetter(14), doc='Scenario probabilities')


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

    Pd = property(itemgetter(0), doc='Power sold in the day-ahead market')
    Pa = property(itemgetter(1), doc='Power traded in the adjustment market')
    Ps = property(itemgetter(2), doc='Final power schedule')
    desvP = property(itemgetter(3), doc='Positive energy deviation')
    desvN = property(itemgetter(4), doc='Negative energy deviation')
    var = property(itemgetter(5), doc='Value-at-risk')
    eta = property(itemgetter(6), doc='Auxiliary variable')


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
                            distribution[d][l][a][w][k] = self.inp.dt * self.inp.lambdaD[d] * self.variables.Pd[d] \
                                                          + self.inp.dt * self.lambdaI[d][a] * self.variables.Pa[d][l] \
                                                          + self.inp.lambdaD[d] * self.inp.r_pos[k] * \
                                                            self.variables.desvP[d][l][w] \
                                                          - self.inp.lambdaD[d] * self.inp.r_neg[k] * \
                                                            self.variables.desvN[d][l][w]

        return distribution

    def expected_profit(self):
        return np.sum(self.profit_distribution() * self.inp.pi)

    def profit_std(self):
        return np.sqrt(np.sum((self.profit_distribution() - self.expected_profit()) ** 2 * \
                              self.inp.pi))

    def cvar(self):
        return self.variables.var - \
               np.sum(self.inp.pi * self.variables.eta) / (1 - self.inp.alfa)

    def print_output(self):
        print "beta: ", self.inp.beta
        print 'expected profit: %.2f' % self.expected_profit()
        print 'profit standard deviation: %.2f' % self.profit_std()
        print 'CVaR: %.2f' % self.cvar()
        print 'power sold in the day-ahead market'
        np.savetxt(sys.stdout, self.variables.Pd, fmt='%7.1f')
        print 'power traded in the adjustment market'
        np.savetxt(sys.stdout, self.variables.Pa, fmt='%7.1f')
        print 'final power schedule'
        np.savetxt(sys.stdout, self.variables.Ps, fmt='%7.1f')
        print 'initialization time: %.2fs, solver time: %.2fs' % \
              (self.internals.elapsed['initialization_time'], self.internals.elapsed['solver_time'])


class Optimizator():
    def __call__(self, *args):
        return self.optimize(args[0])

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
    def optimize(inp):
        lambdaI = inp.lambdaD.reshape(inp.D, 1) + inp.MAvsMD.reshape(1, inp.A)

        variables = Optimizator._make_variables(inp)
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
    def _make_variables(inp):

        Pd = []  # Pd(D) Power sold in the day-ahead market
        for d in xrange(inp.D):
            Pd.append(oovar("Pd(%d)" % (d), lb=0, ub=inp.Pmax))

        Pa = []  # Pa(D,L) Power traded in the adjustment market
        for d in xrange(inp.D):
            Pa.append([])
            for l in xrange(inp.L):
                Pa[d].append(oovar("Pa(%d,%d)" % (d, l)))

        Ps = []  # Ps(D,L) Final power schedule
        for d in xrange(inp.D):
            Ps.append([])
            for l in xrange(inp.L):
                Ps[d].append(oovar("Ps(%d,%d)" % (d, l), lb=0, ub=inp.Pmax))

        desvP = []  # desvP(D,L,W) Positive energy deviation
        for d in xrange(inp.D):
            desvP.append([])
            for l in xrange(inp.L):
                desvP[d].append([])
                for w in xrange(inp.W):
                    desvP[d][l].append(oovar("desvP(%d,%d,%d)" % (d, l, w), lb=0))

        desvN = []  # desvN(D,L,W) Negative energy deviation
        for d in xrange(inp.D):
            desvN.append([])
            for l in xrange(inp.L):
                desvN[d].append([])
                for w in xrange(inp.W):
                    desvN[d][l].append(oovar("desvN(%d,%d,%d)" % (d, l, w), lb=0))

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
                            profit = inp.dt * inp.lambdaD[d] * var.Pd[d] \
                                     + inp.dt * lambdaI[d][a] * var.Pa[d][l] \
                                     + inp.lambdaD[d] * inp.r_pos[k] * var.desvP[d][l][w] \
                                     - inp.lambdaD[d] * inp.r_neg[k] * var.desvN[d][l][w]
                            profit_exp += inp.pi[d][l][a][w][k] * profit
                            cvar_sum += inp.pi[d][l][a][w][k] * var.eta[d][l][a][w][k]
        obj = profit_exp + inp.beta * (var.var - cvar_sum / (1 - inp.alfa))

        logging.debug("obj = %s", obj.expr)
        return obj


    @staticmethod
    def _make_constraints(inp, var, lambdaI):
        constraints = []

        # DesvDEF(D,L,W).. desvP(D,L,W)-desvN(D,L,W) =e= dt*(P(L,W) - Ps(D,L));
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    cons_part.append(var.desvP[d][l][w] - var.desvN[d][l][w] == inp.dt * (inp.P[l][w] - var.Ps[d][l]))
        constraints.extend(cons_part)

        logging.debug("DesvDEF = \n%s", "\n".join([x.expr for x in cons_part]))

        # MAXdesvPOS(D,L,W).. desvP(D,L,W) =l= P(L,W)*dt;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    cons_part.append(var.desvP[d][l][w] < inp.dt * inp.P[l][w])
        constraints.extend(cons_part)

        logging.debug("MAXdesvPOS = \n%s", "\n".join([x.expr for x in cons_part]))

        # MAXdesvNEG(D,L,W).. desvN(D,L,W) =l= Pmax*dt;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    cons_part.append(var.desvN[d][l][w] < inp.dt * inp.Pmax)
        constraints.extend(cons_part)

        logging.debug("MAXdesvNEG = \n%s", "\n".join([x.expr for x in cons_part]))

        # PsDEF(D,L).. Ps(D,L) =e= Pd(D) + Pa(D,L);
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                cons_part.append(var.Ps[d][l] == var.Pd[d] + var.Pa[d][l])
        constraints.extend(cons_part)

        logging.debug("PsDEF = \n%s", "\n".join([x.expr for x in cons_part]))

        # curve(D,Daux)$(lambdaD(Daux) GT lambdaD(D)).. Pd(D)-Pd(Daux) =l= 0;
        cons_part = []
        for d in xrange(inp.D):
            for daux in xrange(inp.D):
                if d != daux and inp.lambdaD[daux] > inp.lambdaD[d]:
                    cons_part.append(var.Pd[d] - var.Pd[daux] < 0)
        constraints.extend(cons_part)

        logging.debug("curve = \n%s", "\n".join([x.expr for x in cons_part]))

        # noANTICIPd(D,Daux)$(lambdaD(Daux) EQ lambdaD(D)).. Pd(D) =e= Pd(Daux);
        cons_part = []
        for d in xrange(inp.D):
            for daux in xrange(inp.D):
                if d != daux and inp.lambdaD[daux] == inp.lambdaD[d]:  # TODO: badness is obvious
                    cons_part.append(var.Pd[d] == var.Pd[daux])
        constraints.extend(cons_part)

        logging.debug("noANTICIPd = \n%s", "\n".join([x.expr for x in cons_part]))

        # CVaRrest(D,L,A,W,K).. var - profit(D,L,A,W,K) - eta(D,L,A,W,K) =l= 0;
        cons_part = []
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            profit = inp.dt * inp.lambdaD[d] * var.Pd[d] \
                                     + inp.dt * lambdaI[d][a] * var.Pa[d][l] \
                                     + inp.lambdaD[d] * inp.r_pos[k] * var.desvP[d][l][w] \
                                     - inp.lambdaD[d] * inp.r_neg[k] * var.desvN[d][l][w]
                            cons_part.append(var.var - profit - var.eta[d][l][a][w][k] < 0)
        constraints.extend(cons_part)

        logging.debug("CVaRrest = \n%s", "\n".join([x.expr for x in cons_part]))

        logging.debug("constraints = \n%s", "\n".join([x.expr for x in constraints]))
        return constraints


    @staticmethod
    def _make_start_point(inp, var):
        start_point = {}
        for d in xrange(inp.D):
            start_point[var.Pd[d]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                start_point[var.Pa[d][l]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                start_point[var.Ps[d][l]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    start_point[var.desvP[d][l][w]] = 0

        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    start_point[var.desvN[d][l][w]] = 0

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
        Pd = np.empty((inp.D))
        for d in xrange(inp.D):
            Pd[d] = x[var.Pd[d]]

        Pa = np.empty((inp.D, inp.L))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                Pa[d][l] = x[var.Pa[d][l]]

        Ps = np.empty((inp.D, inp.L))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                Ps[d][l] = x[var.Ps[d][l]]

        desvP = np.empty((inp.D, inp.L, inp.W))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    desvP[d][l][w] = x[var.desvP[d][l][w]]

        desvN = np.empty((inp.D, inp.L, inp.W))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for w in xrange(inp.W):
                    desvN[d][l][w] = x[var.desvN[d][l][w]]

        xi = x[var.var]
        eta = np.empty((inp.D, inp.L, inp.A, inp.W, inp.K))
        for d in xrange(inp.D):
            for l in xrange(inp.L):
                for a in xrange(inp.A):
                    for w in xrange(inp.W):
                        for k in xrange(inp.K):
                            eta[d][l][a][w][k] = x[var.eta[d][l][a][w][k]]

        return Variables(Pd=Pd, Pa=Pa, Ps=Ps, desvP=desvP, desvN=desvN, var=xi, eta=eta)


def test():
    D = 2
    L = 2
    A = 2
    W = 2
    K = 2

    inp = Input(D=D, L=L, A=A, W=W, K=K,
                dt=1.0,
                Pmax=100.0,
                alfa=0.95,
                beta=0,
                P=np.array([[100, 50], [0, 40]]),
                lambdaD=np.array([50, 20]),
                MAvsMD=np.array([-10, 3]),
                r_pos=np.array([1, 0.9]),
                r_neg=np.array([1.5, 1]),
                pi=np.array([0.0098, 0.0042, 0.0294, 0.0126, 0.0182, 0.0078, 0.0546, 0.0234, 0.0343, 0.0147,
                             0.0245, 0.0105, 0.0637, 0.0273, 0.0455, 0.0195, 0.0147, 0.0063, 0.0441, 0.0189,
                             0.0273, 0.0117, 0.0819, 0.0351, 0.05145, 0.02205, 0.03675, 0.01575, 0.09555, 0.04095,
                             0.06825, 0.02925]).reshape((D, L, A, W, K))
    )
    result = Optimizator()(inp)
    print result.inp
    print result.variables
    result.print_output()


if __name__ == '__main__':
    test()
