import matplotlib.pyplot as plt
from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.faultsource import FaultSource
import numpy as np

# Define layers as per the Perl script
layers_data = [
    (5.5, 3.18, 1.730, 1.730 / 3.18, 600, 600),
    (10.5, 3.64, 1.731, 1.731 / 3.64, 600, 600),
    (16.0, 3.87, 1.731, 1.731 / 3.87, 600, 600),
    (90.0, 4.50, 1.733, 1.733 / 4.50, 900, 900),
    (0.00, 4.50, 1.733, 1.733 / 4.50, 900, 900)  # Adding a half-space layer
]


# Create crust model
crust_model = CrustModel(len(layers_data))
for layer_data in layers_data:
    crust_model.add_layer(*layer_data)

# Create point source
# Assuming strike, dip, and rake from your syn command as an example
strike, dip, rake = 355, 80, -70
source = PointSource([0, 0, 15], [strike, dip, rake])
fault = FaultSource([source], metadata={"name": "single-point-source"})

# Create stations at specified distances
distances_km = [50]  # Selecting only the 50 km station as in your syn example
stations_list = [Station([dist, 0, 0]) for dist in distances_km]
print(f"Simulating... {len(stations_list)} Stations")
stations = StationList(stations_list, metadata={"name": "station_list"})

# Create ShakerMaker instance and run simulation
shaker = shakermaker.ShakerMaker(crust_model, fault, stations)
shaker.run(
    dt=0.1,   # Output time-step
    nfft=256,  # N timesteps
    dk=0.3,     # wavenumber discretization
    tb=51.2     # Initial zero-padding
)

# Plot and save results for the single station
#station = stations[0]
for i, station in enumerate(stations):
    plt.figure()
    z, e, n, t = station.get_response()
    plt.plot(t, z, label='Z')
    plt.plot(t, e, label='E')
    plt.plot(t, n, label='N')
    plt.legend()
    plt.title(f'Station at {distances_km[i]} km')
    # Define a tolerance value
    tolerance = 1e-3  # You can adjust this value based on your data
    # Find the last index where both lines are close to zero
    last_index = np.where((np.abs(z) < tolerance) & (np.abs(e) < tolerance))[0][-1]
    # Limit the x-axis to this range
    plt.xlim([0, 21])
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    # plt.savefig(f'output_plot_{distances_km[i]}km.png')
    plt.show()
