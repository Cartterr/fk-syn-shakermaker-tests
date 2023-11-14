from scipy.integrate import cumulative_trapezoid
from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.tools.plotting import ZENTPlot
from shakermaker.stf_extensions import Brune
import numpy as np

# Source Mechanism
ϕ, θ, λ = 0., 90., 0.    # Strike, dip, rake angles

# Source Time Function
t0, f0 = 0., 5.  # Corner frequency set to 5 Hz as per the fk.pl command
stf = Brune(f0=f0, t0=t0)

# Create a Point Source at a depth of 15 km
source_depth = 15
source = PointSource([0, 0, source_depth], [ϕ, θ, λ], tt=0, stf=stf)

# Assuming the 'hk' model is a predefined crust model
# (This part would need modification to represent the exact layers of the 'hk' model)
corteza = CrustModel(1)
espesor = 0
corteza.add_layer(espesor, 6.000, 3.500, 2.700, 10000., 20000.)

# Create stations at distances from 05 to 80 km at intervals of 5 km
stations = []
for dist in np.arange(5, 85, 5):  # From 5 to 80 km
    station = Station([dist, 0, 0], metadata={"name": f"Station_{dist}", "filter_results": False, "filter_parameters": {"fmax": 5.}})
    stations.append(station)
station_list = StationList(stations)

# Create the ShakerMaker model and run the simulation
modelo = shakermaker.ShakerMaker(corteza, source, station_list)
modelo.run(dt=0.1, nfft=512, dk=0.1, tb=51.2)

def compute_and_compare_integral(estacion):
    # Extract data directly from the Station object using get_response()
    z, e, n, t = estacion.get_response()

    # Manually calculate velocity by integrating acceleration
    v_integral_e = cumulative_trapezoid(e, t, initial=0)
    v_integral_n = cumulative_trapezoid(n, t, initial=0)
    v_integral_z = cumulative_trapezoid(z, t, initial=0)

    # Manually calculate displacement by integrating the manually-calculated velocity
    d_integral_e = cumulative_trapezoid(v_integral_e, t, initial=0)
    d_integral_n = cumulative_trapezoid(v_integral_n, t, initial=0)
    d_integral_z = cumulative_trapezoid(v_integral_z, t, initial=0)

    # Print the final integrated values for comparison
    print(f"Results for {estacion.metadata['name']}")
    print("--------------------------------------")
    print(f"Velocity (E): Manual Integral: {v_integral_e[-1]:.4f}")
    print(f"Velocity (N): Manual Integral: {v_integral_n[-1]:.4f}")
    print(f"Velocity (Z): Manual Integral: {v_integral_z[-1]:.4f}")
    print(f"Displacement (E): Manual Integral: {d_integral_e[-1]:.4f}")
    print(f"Displacement (N): Manual Integral: {d_integral_n[-1]:.4f}")
    print(f"Displacement (Z): Manual Integral: {d_integral_z[-1]:.4f}")
    print("\n")

# Visualize results for all stations
for station in stations:
    compute_and_compare_integral(station)
    ZENTPlot(station, show=True)
