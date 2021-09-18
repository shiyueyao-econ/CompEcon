# This module has tools to solve ordinary differential equations



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from compecon import BasisChebyshev, BasisSpline, NLP, jacobian


class ode:
    def __init__(self, f, T, bv, *params):
        self.f = lambda x: f(x, *params)
        self.T = T
        self.bv = bv
        self._d = len(self.bv)
        self.fsol = None

    def solve_collocation(self, *, n=100, bt=None, bx=None, btype='cheb', c=None, nf=10):
        if bt is None:
            bt = np.zeros_like(self.bv)
        if bx is None:
            bx = np.arange(len(self.bv))

        basis = BasisChebyshev if btype.lower() == 'cheb' else BasisSpline

        # compute collocation nodes
        t = basis(n - 1, 0, T).nodes

        # Approximation structure
        labels = [f'$x_{j}$' for j in range(self._d)]
        self.fsol = basis(n, 0, T, l=labels, labels=['Time'])  # falta inicializar los coeficientes

        # residual function for nonlinear problem formulation
        def residual(c):
            # reshape coefficient vector
            self.fsol.c = c.reshape(self._d, n)

            # compute residuals at nodal times
            x = self.fsol(t)
            dx = self.fsol(t, 1)
            r = dx - self.f(x)

            # compute residuals at boundaries
            x = self.fsol(bt)
            b = np.array([x[j, bx[j]] - self.bv[j] for j in range(self._d)])
            b = np.atleast_2d(b).T
            return np.c_[r, b].flatten()

        # Solve the nonlinear system
        self.fsol.c = NLP(residual).broyden(x0=self.fsol.c.flatten()).reshape(self._d, n)

        # Compute solution at plotting nodes
        if nf > 0:
            m = int(nf) * n
            t = np.linspace(0, T, m)
        else:
            t = t.flatten()

        x = self.fsol(t)

        # Compute residual
        dx = self.fsol(t, 1)
        resid = dx - self.f(x)

        self.x = pd.DataFrame(x.T, index=t, columns=labels)
        self.resid = pd.DataFrame(resid.T, index=t, columns=labels)

    def rk4(self, n=1000, xnames=None):
        t = np.linspace(0, self.T, n)
        x0 = np.asarray(self.bv)

        x = np.zeros((n, self._d), float)

        x[0] = x0
        h = np.r_[0, t[1:] - t[:-1]]
        for i, hh in enumerate(h[1:], start=1):
            f1 = self.f(x0) * (hh / 2)
            f2 = self.f(x0 + f1) * hh
            f3 = self.f(x0 + f2 / 2) * hh
            f4 = self.f(x0 + f3) * (hh / 2)
            x0 = x0 + (f1 + f2 + f3 + f4) / 3
            x[i] = x0

        self.x = pd.DataFrame(x, index=t, columns=xnames)
        # self.resid = pd.DataFrame(resid.T, index=t, columns=labels)

    def spx(self, x0=None, T=None, n=1000):

        f = self.f
        if x0 is None:
            x0 = self.bv

        if T is None:
            T = self.T

        J = jacobian(f, x0)
        D, V = np.linalg.eig(J)
        i = D < 0
        j = D > 0

        # if np.iscomplex(D).any() or i.any():
        #    print('x is not saddle point or stable steady-state')   #todo review, make warning
        #    x = []
        #    return x

        i = np.argmin(D)
        delx = 0.0001 * V[:, i]  # eigenvector asociated with minimum eigenvalue
        t = np.linspace(0, -T, n)
        h = t[1:] - t[:-1]

        # xsp
        xsp = np.zeros((n, 2))
        x = x0 + delx

        xsp[0] = x
        for i, hh in enumerate(h, start=1):
            f1 = f(x) * (hh / 2)
            f2 = f(x + f1) * hh
            f3 = f(x + f2 / 2) * hh
            f4 = f(x + f3) * (hh / 2)
            x += (f1 + f2 + f3 + f4) / 3
            xsp[i] = x

        # xsp(i+1:n,:) = []; parece innecesario
        xsp = np.real(xsp)

        # xsn
        xsn = np.zeros((n, 2))
        x = x0 - delx

        xsp[0] = x
        for i, hh in enumerate(h, start=1):
            f1 = f(x) * (hh / 2)
            f2 = f(x + f1) * hh
            f3 = f(x + f2 / 2) * hh
            f4 = f(x + f3) * (hh / 2)
            x += (f1 + f2 + f3 + f4) / 3
            xsn[i] = x

        # xsn(i+1:n,:) = []; parece innecesario
        xsn = np.real(xsn)

        x = np.r_[xsn[::-1], np.atleast_2d(x0), xsp]
        j = np.isfinite(x).all(axis=1)

        return x[j]