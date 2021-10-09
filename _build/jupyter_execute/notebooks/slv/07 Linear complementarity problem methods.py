#!/usr/bin/env python
# coding: utf-8

# # Linear complementarity problem methods
# 
# **Randall Romero Aguilar, PhD**
# 
# This demo is based on the original Matlab demo accompanying the  <a href="https://mitpress.mit.edu/books/applied-computational-economics-and-finance">Computational Economics and Finance</a> 2001 textbook by Mario Miranda and Paul Fackler.
# 
# Original (Matlab) CompEcon file: **demslv07.m**
# 
# Running this file requires the Python version of CompEcon. This can be installed with pip by running
# 
#     !pip install compecon --upgrade
# 
# <i>Last updated: 2021-Oct-01</i>
# <hr>
# 

# In[1]:


import numpy as np
from compecon import LCP, tic, toc


# ### Generate problem test data

# In[2]:


n = 8
z = np.random.randn(n, 2) - 1


# ### Boundaries

# In[3]:


a = np.min(z, 1)
b = np.max(z, 1)


# ### Objective function

# In[4]:


q = np.random.randn(n)
M = np.random.randn(n, n)
M = - np.dot(M.T, M)


# ### Define the problem by creating an LCP instance

# In[5]:


L = LCP(M, q, a, b)


# ### Set 100 random initial points

# In[6]:


nrep = 100
x0 = np.random.randn(nrep, n)


# ### Solve by applying Newton method to semi-smooth formulation

# In[7]:


t0 = tic()
it1 = 0
L.opts.transform = 'ssmooth'
for k in range(nrep):
    L.newton(x0[k])
    it1 += L.it
t1 = toc(t0)
n1 = L.fnorm


# ### Solve by applying Newton method to minmax formulation

# In[8]:


t0 = tic()
it2 = 0
L.opts.transform = 'minmax'
for k in range(nrep):
    L.newton(x0[k])
    it2 += L.it
t2 = toc(t0)
n2 = L.fnorm


# ### Print results

# In[9]:


print('Hundredths of seconds required to solve randomly generated linear \n',
      'complementarity problem on R^8 using Newton and Lemke methods')
print('\nAlgorithm           Time      Norm   Iterations  Iters/second\n' + '-' * 60)
print('Newton semismooth {:6.2f}  {:8.0e}   {:8d}  {:8.1f}'.format(t1, n1, it1, it1/t1))
print('Newton minmax     {:6.2f}  {:8.0e}   {:8d}  {:8.1f}'.format(t2, n2, it2, it2/t2))

