'''
Created on May 20, 2013

@author: Steven
'''
import matplotlib

matplotlib.use('Agg')
import matplotlib.ticker as tick
from hmf import Perturbations
import matplotlib.gridspec as gridspec

from matplotlib import pyplot as plt

import numpy as np

plt.rc('font', size=16)
directory = '/Users/Steven/Documents/PhD/Products/hmf-web-app/'  # '/Users/Steven/Documents/PhD/Products/RIPPLES Poster 2013/'
xlab = r'Mass M$_\odot h^{-1}$'

# ===============================================================================
# Power Spectrum
# ===============================================================================
# pert = Perturbations(M, n=1)
#
# powern1 = pert.power_spectrum
# massvn1 = pert.sigma
#
# pert.update(n=0.8)
# powern8 = pert.power_spectrum
# massvn8 = pert.sigma
# plt.grid(True)
# plt.ylabel("Power")
# plt.xlabel("Wavenumber")
# plt.plot(np.exp(pert.k), np.exp(powern1), label="n = 1")
# plt.plot(np.exp(pert.k), np.exp(powern8), label="n = 0.8")
# plt.xscale('log')
# plt.yscale('log')
# plt.legend(loc=0)
# plt.tight_layout()
# plt.savefig(directory + 'power_spec.eps')

# ===============================================================================
# Mass Variance
# ===============================================================================
# plt.clf()
# plt.grid(True)
# plt.ylabel(r'Mass Variance, $\sigma^2$')
# plt.xlabel(xlab)
# plt.plot(10 ** M, massvn1 ** 2, label="n = 1")
# plt.plot(10 ** M, massvn8 ** 2, label="n = 0.8")
# plt.legend(loc=0)
# plt.xscale('log')
# plt.tight_layout()
# plt.savefig(directory + 'sigma.eps')


# ===============================================================================
# fsigma and fsigma (Compare) one on the other
# ===============================================================================
plt.clf()
M = np.linspace(10, 15, 501)
fig = plt.figure(figsize=(12 * 1.2, 7.0 * 1.2))
gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])

ax = [plt.subplot(gs[1])]
ax.insert(0, plt.subplot(gs[0], sharex=ax[0]))

ax[0].grid(True)
ax[1].grid(True)
pert = Perturbations(M)

vfv_ST = pert.fsigma
approaches = ['PS', 'ST', 'Jenkins', 'Reed03', 'Warren', 'Reed07', 'Tinker', 'Crocce',
              'Courtin', 'Bhattacharya', 'Angulo', 'Angulo_Bound', 'Watson_FoF', 'Watson',
              "Peacock", "Behroozi"]
lines = ["-", "--", "-.", ":"]

ax[1].set_xlabel(xlab)
ax[0].set_ylabel(r'Fraction of Mass Collapsed, $f(\sigma)$')
ax[1].set_ylabel(r'$f(\sigma)/f_{\rm ST}(\sigma)$')
for i, approach in enumerate(approaches):
    pert.update(mf_fit=approach)
    ax[0].plot(10 ** M, pert.fsigma, label=approach.replace("_", " "), linestyle=lines[(i / 7) % 4])
    ax[1].plot(10 ** M, pert.fsigma / vfv_ST, linestyle=lines[(i / 7) % 4])

ax[0].set_xscale('log')
ax[1].set_xscale('log')
ax[1].set_yscale('log', basey=2)
ax[1].yaxis.set_major_formatter(tick.ScalarFormatter())
ticks = ax[0].yaxis.get_ticklocs()
ax[0].yaxis.set_major_locator(tick.FixedLocator(ticks[1:]))
# ax[0].xaxis.set_major_locator(tick.FixedLocator([]))
# plt.legend(loc=0)
# plt.tight_layout()
plt.subplots_adjust(hspace=0.02, wspace=0.0)
plt.setp(ax[0].get_xticklabels(), visible=False)
box = ax[0].get_position()
ax[0].set_position([box.x0, box.y0, box.width * 0.7, box.height])
ax[0].legend(loc='center left', bbox_to_anchor=(1, 0.25))
box1 = ax[1].get_position()
ax[1].set_position([box1.x0, box1.y0, box1.width * 0.7, box1.height])

plt.savefig(directory + 'f.pdf')

# plt.clf()
# ax = plt.figure(figsize=(12, 7)).add_subplot(111)
# plt.grid(True)
# plt.xlabel(xlab)
#
# ps = pert.MassFunction(fsigma='PS')
# for i, approach in enumerate(approaches):
#    mf = pert.MassFunction(fsigma=approach)
#    plt.plot(10 ** M, mf / ps, label=approach, linestyle=lines[(i / 7) % 4])
#
# plt.xscale('log')
# plt.yscale('log', basey=2)
##plt.legend(loc=0)
##plt.tight_layout()
# ax.yaxis.set_major_formatter(tick.ScalarFormatter())
# box = ax.get_position()
# ax.set_position([box.x0, box.y0, box.width * 0.6, box.height])
# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.savefig(directory + 'comparison_f.eps')

# ===============================================================================
# HMF with comparison side-by-side
# ===============================================================================
# plt.clf()
# fig, axs = plt.subplots(1, 2)
# fig.set_size_inches(19 * 1, 7 * 1)
#
# fs = 18
# axs[0].grid(True)
# axs[1].grid(True)
#
# pert = Perturbations(M)
# approaches = ['PS', 'ST', 'Jenkins', 'Reed03', 'Warren', 'Reed07', 'Tinker', 'Crocce',
#              'Courtin', 'Bhattacharya', 'Angulo', 'Angulo_Bound', 'Watson_FoF', 'Watson']
# lines = ["-", "--", "-.", ":"]
#
# axs[0].set_xlabel(xlab, fontsize=fs)
# axs[0].set_ylabel(r'Mass Function $\left( \frac{dn}{d \ln M} \right) h^3 Mpc^{-3}$', fontsize=fs)
# axs[1].set_xlabel(xlab, fontsize=fs)
# axs[1].set_ylabel(r'Ratio of Mass Functions $ \left(\frac{dn}{d \ln M}\right) / \left( \frac{dn}{d \ln M} \right)_{PS} $', fontsize=fs)
#
#
# mf_0 = mf = pert.MassFunction(fsigma="PS")
# for i, approach in enumerate(approaches):
#    mf = pert.MassFunction(fsigma=approach)
#    axs[0].plot(10 ** M, mf, label=approach.replace("_", "-"), linestyle=lines[(i / 7) % 4])
#    axs[1].plot(10 ** M, mf / mf_0, label=approach.replace("_", "-"), linestyle=lines[(i / 7) % 4])
# axs[0].set_xscale('log')
# axs[0].set_yscale('log')
# axs[1].set_xscale('log')
# axs[1].set_yscale('log', basey=2)
# axs[1].yaxis.set_major_locator(tick.FixedLocator([0.5, 0.75, 1, 1.5, 2]))
# axs[1].yaxis.set_major_formatter(tick.ScalarFormatter())
# axs[1].set_ylim((0.5, 2.3))
# box1 = axs[0].get_position()
# axs[0].set_position([box1.x0, box1.y0, box1.width * 0.85, box1.height])
#
# box2 = axs[1].get_position()
# axs[1].set_position([box2.x0 * 0.95, box2.y0, box2.width * 0.85, box2.height])
# axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=fs)
# plt.savefig(directory + 'HMFandCompare.pdf')
# ===============================================================================
# redshift dependence
# ===============================================================================
# plt.clf()
# plt.grid(True)
# plt.xlabel(xlab)
# plt.ylabel(r'Mass Function $\left( \frac{dn}{d \ln M} \right) h^3 Mpc^{-3}$')
# for z in [0.0, 1.0, 5.0]:
#    pert.update(z=z)
#    mf = pert.MassFunction()
#    plt.plot(10 ** M, mf, label="z = " + str(int(z)))
# plt.xscale('log')
# plt.yscale('log')
# plt.legend(loc=0)
# plt.tight_layout()
# plt.savefig(directory + 'hmfz.eps')

# ===============================================================================
# WDM dependence
# ===============================================================================
# plt.clf()
# plt.figure(figsize=(12, 6))
# plt.grid(True)
# M = np.linspace(8, 14, 601)
# pert = Perturbations(M)
#
# plt.xlabel(xlab)
# plt.ylabel(r'Mass Function $\left( \frac{dn}{d \ln M} \right) h^3 Mpc^{-3}$')
# plt.plot(10 ** M, pert.dndlnm, label='CDM')
# for wdm in [0.5, 1.0, 2.0]:
#    pert.update(wdm_mass=wdm)
#    plt.plot(10 ** M, pert.dndlnm, label='WDM = ' + str(wdm))
# plt.xscale('log')
# plt.yscale('log')
# plt.legend(loc=0)
# plt.tight_layout()
# plt.savefig(directory + 'hmfwdm.pdf')

# ===============================================================================
# Finite Box
# ===============================================================================
# plt.clf()
# plt.grid(True)
# ax = plt.figure().add_subplot(111)
# plt.grid(True)
# M = np.linspace(10, 15, 501)
# pert = Perturbations(M)
#
# plt.xlabel(xlab)
# plt.ylabel(r'Ratio of Mass Functions, $\frac{dn}{d\ln M}/(\frac{dn}{d\ln M})_0$')
# base = pert.dndlnm
# for i, min_k in enumerate([0.00000001, 0.1257, 0.0628, 0.02513, 0.01257]):
#    boxsize = ["\infty", '50', '100', '250', '500']
#    pert.update(k_bounds=[min_k, 2000.0])
#    plt.plot(10 ** M, pert.dndlnm / base, label=r'$L = %s$' % (boxsize[i]))
# plt.yscale('log', basey=2)
# plt.xscale('log')
# plt.ylim((0.75, 1.75))
# plt.xlim((10 ** 10, 10 ** 15))
#
# plt.legend(loc=0)
# plt.tight_layout()
# ax.yaxis.set_major_locator(tick.FixedLocator([0.75, 1, 1.25, 1.5, 1.75]))
# ax.yaxis.set_major_formatter(tick.ScalarFormatter())
# plt.savefig(directory + 'boxsize.pdf')

# ===============================================================================
# How Big
# ===============================================================================
# plt.clf()
# plt.figure(figsize=(12, 6))
# plt.grid(True)  #, which='major', color='black', linestyle='-')
##plt.grid(True, which='minor', linestyle='-', color='gray', lw=0.1)
# M = np.linspace(10, 16, 601)
#
# pert = Perturbations(M)
# L = pert.how_big
#
# plt.plot(10 ** M, L, lw=3)
# plt.xlabel(xlab)
# plt.ylabel(r'Box Size, L (Mpc$h^{-1}$)')
# plt.yscale('log')
# plt.xscale('log')
# plt.tight_layout()
# plt.savefig(directory + 'L.pdf')
#
##===============================================================================
## How Many
##===============================================================================
# plt.clf()
# plt.grid(True)  #, which='major', color='black', linestyle='-')
##plt.grid(True, which='minor', linestyle='-', color='gray', lw=0.2)
# sizes = [50, 100, 250, 500, 1000]
# for size in sizes:
#    plt.plot(10 ** M, size ** 3 * pert.ngtm, label=r'$L =$ ' + str(size) + r'Mpc$h^{-1}$')
#
# plt.xlabel(xlab)
# plt.ylabel(r'Expected Number of Haloes')
# plt.yscale('log')
# plt.xscale('log')
# plt.ylim((10 ** -3, 10 ** 8))
# plt.legend(loc=0, fancybox=True)
# plt.tight_layout()
# plt.savefig(directory + 'how_many.pdf')
