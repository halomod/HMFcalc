from hmf import MassFunction
import os
import pickle

staticdir = os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0]
print staticdir
h = MassFunction(mf_fit="Tinker08",transfer_fit = "FromFile",transfer_options={"fname":os.path.join(staticdir,"transfers/PLANCK_transfer.dat")},
              Mmax=15,
              Mmin=10,
              dlog10m=0.05)

h.ngtm
h.rho_ltm
h.rho_gtm

with open("initialmodel.pickle","w") as f:
    pickle.dump(h,f)
