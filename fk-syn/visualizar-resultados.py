import matplotlib.pyplot as plt
import obspy
from scipy.integrate import cumulative_trapezoid

def visualize_and_integrate_sac(filename):
    # Read SAC file
    st = obspy.read(filename)

    print("\n")
    print(st)
    print("\n")
    
    # Extract data and times
    data = st[0].data
    times = st[0].times()

    print("\n")
    print(data)
    print("\n")
    print(times)
    print("\n")

    # Compute integral using the trapezoidal rule
    integral = cumulative_trapezoid(data, times, initial=0)

    # Display the final integrated value with higher precision
    print(f"Final integrated value for {filename}: {integral[-1]:.15f}")

    # Plot original waveform and its integral
    fig, axes = plt.subplots(2, 1, figsize=(8, 6))
    
    # Original waveform
    axes[0].plot(times, data, label='Waveform')
    axes[0].set_title(f'Waveform: {filename}')
    axes[0].set_ylabel('Amplitude')
    axes[0].legend()

    # Integral
    axes[1].plot(times, integral, label='Integral', color='r')
    axes[1].set_title(f'Integral: {filename}')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylabel('Cumulative amplitude')
    axes[1].legend()
    
    plt.savefig('fortran_output_plot1.png')
    plt.tight_layout()
    plt.show()


# Visualize and integrate the PAS.e and PAS.n files
visualize_and_integrate_sac("PAS.e")
visualize_and_integrate_sac("PAS.n")
