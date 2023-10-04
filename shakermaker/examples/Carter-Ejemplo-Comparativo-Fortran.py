import shakermaker
import numpy as np
from shakermaker.crustmodel import CrustModel
from shakermaker.faultsource import FaultSource  # Assuming you have this
from shakermaker.stationlist import StationList  # Assuming you have this
from shakermaker.tools.plotting import ZENTPlot

# Earth model parameters
thicknesses = [5.5, 10.5, 16.0, 90.0]
vs = [3.18, 3.64, 3.87, 4.5]
vp = [1.73, 1.731, 1.731, 1.733]
densities = [2.71, 2.75, 2.81, 3.2]

# Source parameters
depth = 10.0  # in km
magnitude = 5.0
strike = 45.0
dip = 45.0
rake = 0.0

# Define the crustal model
cm = CrustModel(len(thicknesses))
for d, v_p, v_s, rho in zip(thicknesses, vp, vs, densities):
    cm.add_layer(d, v_p, v_s, rho, 1000.0, 1000.0)  # Here, Qp and Qs are set to 1000 arbitrarily

# Define the source mechanism
# Here we need to adapt this to create a FaultSource instead of PointSource
source = FaultSource(...)  # You need to define how to create a FaultSource based on your requirements

# Define stations and convert to StationList
stations = [Station(np.array([10.0, 10.0, 0.0]), "S001")]
stations_list = StationList(stations)  # Assuming StationList can be initialized with a list

# Initialize shakermaker with the given crust model
sm = shakermaker.ShakerMaker(cm, source, stations_list)

# The rest of the script remains mostly unchanged...

# Compute the synthetic seismogram
sm.initialize()
dt = 0.01
nt = 1000
sm.compute_synthetic_seismograms(dt, nt)

# Extract synthetic seismogram for plotting
synthetic = sm.get_synthetic(0, "Z")

# Plot the synthetic seismogram using ZENTPlot
ZENTPlot([synthetic], dt, ['Z component'])

# Return the synthetic seismogram for further use
synthetic
