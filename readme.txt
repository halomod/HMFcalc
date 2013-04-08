README

For more extensive notes on this implementation and the HMF in general, see the paper (reference here soon).

This package is a django web-app, implementing the calculation of the halo mass function in as general a way as possible while keeping it easy to use. 

The top-level contains manage.py, a django file which should not be touched. It also contains this readme and a history log. The static subdirectory contains the css and javascript files, as well as an admin subdirectory which is not used in the app as yet (it is there by default with the django package). 

The important subdirectories of the top-level are HMF, which houses the settings and urls.py files, as well as the various templates for the html content. Basically, HMF is to do with the overall running and look of the website. The other subdirectory is hmf_finder, which is the web-app proper. In here are the views (django functions which tell a page what to have on it) and forms (django functions which tell a web-form what to contain) and a utils.py file which connects the views to the actual calculation modules, which are themselves in the hmf_calc package. 

The hmf_calc package consists of three main modules. The driver is FindMF.py. That's the module that utils.py directly connects with. It has one function in it which basically drives all the calcualtions. Secondly, there is SetupFunctions.py, which houses a few functions to import and define the transfer function. Thirdly is the main core of the calculations. It is in Perturbations.py, and houses a Perturbations() class. This class is set up so that the transfer function and a cosmology is input. It initializes the mass variance based on these, and a couple of other useful functions akin to the mass variance. With this object, a method has been defined to calculate the HMF given an appropriate fitting function.
 
