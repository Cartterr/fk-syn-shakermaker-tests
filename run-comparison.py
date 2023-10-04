import subprocess
import os
import matplotlib.pyplot as plt
import obspy
import numpy as np
from scipy.integrate import cumulative_trapezoid
from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.faultsource import FaultSource
from multiprocessing import Process, Manager
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


# Set the directory paths
fk_syn_dir = "./fk-syn"

def run_fortran_scripts(nfft_test, dt, dk):
    subprocess.run(f"./fk.pl -Mhk/15/k -N{nfft_test}/{dt}/1/{dk}/0.3 -P0/1/15 -S2 50", shell=True, cwd=fk_syn_dir)
    subprocess.run(f"./syn -M4.5/355/80/-70 -D1 -A33.5 -OPAS.z -Ghk_15/50.grn.0", shell=True, cwd=fk_syn_dir)


def visualize_sac(filename, ax, scaling_factor=1):
    # Generate the full path to the SAC file
    full_path = os.path.join(fk_syn_dir, filename)

    # Read SAC file
    st = obspy.read(full_path)
    data = st[0].data * scaling_factor
    times = st[0].times()
    ax.plot(times, data, label=f'{filename}')


def run_shakermaker(nfft_test, dt_test, dk_test, results):
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
        dt=dt_test,          # Output time-step
        nfft=nfft_test,  # N timesteps
        dk=dk_test,          # wavenumber discretization
        tb=50,           # Initial zero-padding
        sigma=2,         # Damping rate
        kc=15.0,         # Max wavenumber
        pmin=0,          # Max. phase velocity
        pmax=1,          # Min. phase velocity
        taper=0.3        # Low-pass filter taper
    )

    # Plot and save results for the single station
    # Instead of saving the figure, plot it
    for i, station in enumerate(stations):
        z, e, n, t = station.get_response()
        
    results.extend([z, e, n, t, distances_km, stations])
        

# A function to update the plot based on slider values
def update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig):
    ax.clear()
    ax.set_xlim([0, 35])  # Setting x-axis limits
    
    # Retrieve the current slider values
    dt_fortran = s_dt_fortran.val
    dt_shakermaker = s_dt_shakermaker.val
    nfft_fortran = int(s_nfft_fortran.val)
    nfft_shakermaker = int(s_nfft_shakermaker.val)
    dk_fortran = s_dk_fortran.val
    dk_shakermaker = s_dk_shakermaker.val
    
    # Re-run the Fortran simulations with new parameters
    run_fortran_scripts(nfft_fortran, dt_fortran, dk_fortran)
    
    # Plot the results from the Fortran scripts
    seismic_components = ["e"]
    fk_syn_scale = s_fk_syn_scale.val
    for component in seismic_components:
        visualize_sac(f"PAS.{component}", ax, fk_syn_scale)

    # Re-run the Shakermaker simulations with new parameters
    manager = Manager()
    results = manager.list()
    process = Process(target=run_shakermaker, args=(nfft_shakermaker, dt_shakermaker, dk_shakermaker, results))
    process.start()
    process.join(timeout=1)

    if process.is_alive():
        print("Timed out. Moving to the next nfft.")
        process.terminate()
        process.join()

    # Retrieve the results
    z, e, n, t, distances_km, stations = results
    
    for i, station in enumerate(stations):
        for component in seismic_components:
            if component == "z":
                ax.plot(t, z, label=f'Shakermaker Z at {distances_km[i]} km and nfft={nfft_shakermaker}')
            elif component == "e":
                ax.plot(t, e, label=f'Shakermaker E at {distances_km[i]} km and nfft={nfft_shakermaker}')
            elif component == "n":
                ax.plot(t, n, label=f'Shakermaker N at {distances_km[i]} km and nfft={nfft_shakermaker}')
    
    # Finalize the combined plot
    ax.legend()
    ax.set_title("Combined Plot")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    
    fig.canvas.draw_idle()


# Your main function
def main():
    # Create a new figure for the sliders
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.45)  # Adjust this to make room for sliders
    
    try:
        fig.canvas.manager.window.attributes('-zoomed', True)  # For TkAgg backend, to make the window resizable and maximized
    except AttributeError:
        pass

    # Create sliders with new arrangement
    axcolor = 'lightgoldenrodyellow'
    ax_nfft_fortran = plt.axes([0.25, 0.01, 0.65, 0.03], facecolor=axcolor)
    ax_dt_fortran = plt.axes([0.25, 0.06, 0.65, 0.03], facecolor=axcolor)
    ax_dk_fortran = plt.axes([0.25, 0.11, 0.65, 0.03], facecolor=axcolor)
    ax_nfft_shakermaker = plt.axes([0.25, 0.16, 0.65, 0.03], facecolor=axcolor)
    ax_dt_shakermaker = plt.axes([0.25, 0.21, 0.65, 0.03], facecolor=axcolor)
    ax_dk_shakermaker = plt.axes([0.25, 0.26, 0.65, 0.03], facecolor=axcolor)
    ax_fk_syn_scale = plt.axes([0.25, 0.31, 0.65, 0.03], facecolor=axcolor)

    s_dt_fortran = Slider(ax_dt_fortran, 'dt Fortran', 0.01, 0.2, valinit=0.1)
    s_dt_shakermaker = Slider(ax_dt_shakermaker, 'dt Shakermaker', 0.01, 0.2, valinit=0.1)
    s_nfft_fortran = Slider(ax_nfft_fortran, 'NFFT Fortran', valmin=64, valmax=1024, valinit=256, valstep=[64, 128, 256, 512, 1024])
    s_nfft_shakermaker = Slider(ax_nfft_shakermaker, 'NFFT Shakermaker', valmin=64, valmax=1024, valinit=128, valstep=[64, 128, 256, 512, 1024])
    s_dk_fortran = Slider(ax_dk_fortran, 'dk Fortran', 0.1, 2.0, valinit=0.3)
    s_dk_shakermaker = Slider(ax_dk_shakermaker, 'dk Shakermaker', 0.1, 10.0, valinit=1.89)
    #s_fk_syn_scale = Slider(ax_fk_syn_scale, 'fk_syn_scale', valmin=1e12, valmax=1e14, valinit=1e13, valstep=[1e12, 1e13, 1e14])
    s_fk_syn_scale = Slider(ax_fk_syn_scale, 'fk_syn_scale', valmin=1e12, valmax=1e13, valinit=1)

    # Update the plot when a slider value is changed
    s_dt_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_dt_shakermaker.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_nfft_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_nfft_shakermaker.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_dk_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_dk_shakermaker.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))
    s_fk_syn_scale.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dt_shakermaker, s_nfft_shakermaker, s_dk_fortran, s_dk_shakermaker, s_fk_syn_scale, ax, fig))

    # Show the plot with sliders
    plt.show()


if __name__ == "__main__":
    main()
