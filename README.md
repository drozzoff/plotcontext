# `plottingContext` class

It provides a context manager to set the plotting for an accelerator related data.

Currently, one can add the apertures or survey of the lattice as a background to the plot.

Example of use:

```python
from plotAccelerator import plottingContext
```

```python

plotcontext = PlotContext(show_survey = True, show_apertures = True, line = sis18ring)

with plotcontext as ctx:
	ctx.add_plot(np.linspace(0, 100, 30), np.linspace(-0.020, 0.020, 30), '-o', label = "dummy", color = "green" )

```
Inside of the context one can plot any arbitrary data, and the survey and apertures will be plotted as well if requested.
