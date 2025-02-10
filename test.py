from cpymad.madx import Madx

import xtrack as xt

import numpy as np
from warnings import warn
import matplotlib.pyplot as plt


from plotContext import PlotContext

# changing the reference beam

# some constraints
e0 = 931.49410242e6 # thus is an equivalent of the 1 amu in eV
a_e = 5.48579909065e-4

# this is evaluated taking into account the mass excess in eV
A_4He = 4 + 2424.91587e3 / e0
charge = +1

mass = (A_4He - charge * a_e) * e0
kin_energy = 225.0e6 * 4

print(A_4He, mass)

# helium beam properties

helium_beam_ref_beam = xt.Particles(mass0 = mass, q0 = 3, p0c = kin_energy)

ex_norm = 16e-6
gamma_he = 1 + kin_energy/e0
beta_he =  np.sqrt(1 - 1 / gamma_he**2)

ex = ex_norm / gamma_he

print(f"Horizontal emittance = {ex}")

# 1) creating a pymad object

mad = Madx()
mad.option(echo = False)

mad.call("files/SIS18RING_xtrack.seq")
mad.call("files/SIS18_TAU_1.000.str")

e0 = 931.49410242e-3 # in GeV
energy_he = e0 * gamma_he * 4

print(energy_he)
print(gamma_he, beta_he)
mad.sequence.sis18ring.beam = {
	'particle': "ion",
	'mass': 4 * e0,
	'charge': 1,
	'energy': energy_he,
	
}

mad.use(sequence = 'sis18ring') # honestly no idea why use is needed to assign the beam to a sequence
print(mad.sequence.sis18ring.beam)

mad.call("files/SIS18_cryocatchers.str") # some apertures

# 2) importing pymad sequence into xsuite
xtrack_import_flags = {
	'deferred_expressions': True,
	'install_apertures': True,
	'skip_markers': False,
	'enable_align_errors': True,
}


sis18ring = xt.Line.from_madx_sequence(mad.sequence.sis18ring, **xtrack_import_flags)


# 3) realigning the assymetric apertures
UNLIMITED = 1e10

for name in sis18ring.element_dict:
	element = sis18ring.element_dict[name]
	try:
		if element.shift_x != 0.0:
			if isinstance(element, xt.LimitRect):
#                pass
				print(f"{element.__class__.__name__}, name = '{name}', shift_x = {element.shift_x}\n\t min_x = {element.min_x}, max_x = {element.max_x}, min_y = {element.min_y}, max_y = {element.max_y}")
				
				# modifying the apertures wrt to the offsets
				element.min_x += element.shift_x # lower jaw
				element.max_x += element.shift_x # upper jaw

				# removing 1 of the jaws when it is too larger (abs > 150 mm)
				if abs(element.min_x) > 0.150:
					element.min_x = -UNLIMITED
				if abs(element.max_x) > 0.150:
					element.max_x = UNLIMITED

				element.shift_x = 0.0
				
			elif isinstance(element, xt.LimitEllipse):
				warn("The elliptic aperture is missaligned!")
				print(f"{element.__class__.__name__}, name = '{name}', shift_x = '{element.shift_x}'\n\t a = {element.a}, b = {element.b}")
			else:
				print("Element is not aperture element")
	except AttributeError:
		# elements that do not have shift_x property
		pass
	
plotcontext = PlotContext(show_survey = True, show_apertures = True, line = sis18ring)

with plotcontext as ctx:
	ctx.add_plot(np.linspace(0, 100, 30), np.linspace(-0.020, 0.020, 30), '-o', label = "dummy", color = "green" )

	plt.savefig("test1.pdf")
