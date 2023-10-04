from shakermaker import shakermaker
import numpy as np
from shakermaker.station import Station
from shakermaker.tools.plotting import ZENTPlot
from scipy.integrate import cumulative_trapezoid
import matplotlib.pylab as plt

files = [
    #"resultado_sim0_10km.npz",
    "resultado_s0.npz",
    "resultado_s1.npz",
    "resultado_s2.npz",
    "resultado_s3.npz",
    "resultado_s4.npz",
    "resultado_s5.npz",
    "resultado_s6.npz",
    "resultado_s7.npz",
    "resultado_s8.npz",
    "resultado_s9.npz",
    # "resultado_sim0_20km.npz",
    # "resultado_sim0_10km_2.npz",
   ]

tmax = 50.

for f in files:
    s = Station()
    s.load(f)
    
    z,e,n,t = s.get_response()

    z = z[t<tmax]
    e = e[t<tmax]
    n = n[t<tmax]
    t = t[t<tmax]
    
    dz = cumulative_trapezoid(z.copy(), t, initial=0.)
    de = cumulative_trapezoid(e.copy(), t, initial=0.)
    dn = cumulative_trapezoid(n.copy(), t, initial=0.)
    
    az = np.gradient(z,t)
    ae = np.gradient(e,t)
    an = np.gradient(n,t)
    
    i_PGD_max_z = dz.argmax()
    i_PGD_min_z = dz.argmin()
    i_PGD_max_e = de.argmax()
    i_PGD_min_e = de.argmin()
    i_PGD_max_n = dn.argmax()
    i_PGD_min_n = dn.argmin()
    
    i_PGV_max_z = z.argmax()
    i_PGV_min_z = z.argmin()
    i_PGV_max_e = e.argmax()
    i_PGV_min_e = e.argmin()
    i_PGV_max_n = n.argmax()
    i_PGV_min_n = n.argmin()
    
    i_PGA_max_z = az.argmax()
    i_PGA_min_z = az.argmin()
    i_PGA_max_e = ae.argmax()
    i_PGA_min_e = ae.argmin()
    i_PGA_max_n = an.argmax()
    i_PGA_min_n = an.argmin()
    
    
    plt.subplot(3,3,1)
    plt.plot(t,dz)
    plt.plot(t[i_PGD_max_z], dz[i_PGD_max_z],"o")
    plt.text(t[i_PGD_max_z], dz[i_PGD_max_z],f"{dz[i_PGD_max_z]:.2f}")
    plt.plot(t[i_PGD_min_z], dz[i_PGD_min_z],"o")
    plt.text(t[i_PGD_min_z], dz[i_PGD_min_z],f"{dz[i_PGD_min_z]:.2f}")
    plt.ylabel("$z$")
    plt.title("PGD")
    plt.subplot(3,3,4)
    plt.plot(t,de)
    plt.plot(t[i_PGD_max_e], de[i_PGD_max_e],"o")
    plt.text(t[i_PGD_max_e], de[i_PGD_max_e],f"{de[i_PGD_max_e]:.2f}")
    plt.plot(t[i_PGD_min_e], de[i_PGD_min_e],"o")
    plt.text(t[i_PGD_min_e], de[i_PGD_min_e],f"{de[i_PGD_min_e]:.2f}")
    plt.ylabel("$e$")
    plt.subplot(3,3,7)
    plt.plot(t,dn)
    plt.plot(t[i_PGD_max_n], dn[i_PGD_max_n],"o")
    plt.text(t[i_PGD_max_n], dn[i_PGD_max_n],f"{n[i_PGD_max_n]:.2f}")
    plt.plot(t[i_PGD_min_n], dn[i_PGD_min_n],"o")
    plt.text(t[i_PGD_min_n], dn[i_PGD_min_n],f"{n[i_PGD_min_n]:.2f}")
    plt.ylabel("n")
    plt.xlabel("t (s)")
    
    plt.subplot(3,3,2)
    plt.plot(t,z)
    plt.plot(t[i_PGV_max_z], z[i_PGV_max_z],"o")
    plt.text(t[i_PGV_max_z], z[i_PGV_max_z],f"{z[i_PGV_max_z]:.2f}")
    plt.plot(t[i_PGV_min_z], z[i_PGV_min_z],"o")
    plt.text(t[i_PGV_min_z], z[i_PGV_min_z],f"{z[i_PGV_min_z]:.2f}")
    plt.ylabel("$\\dot{z}$")
    plt.title("PGV")
    plt.subplot(3,3,5)
    plt.plot(t,e)
    plt.plot(t[i_PGV_max_e], e[i_PGV_max_e],"o")
    plt.text(t[i_PGV_max_e], e[i_PGV_max_e],f"{e[i_PGV_max_e]:.2f}")
    plt.plot(t[i_PGV_min_e], e[i_PGV_min_e],"o")
    plt.text(t[i_PGV_min_e], e[i_PGV_min_e],f"{e[i_PGV_min_e]:.2f}")
    plt.ylabel("$\\dot{e}$")
    plt.subplot(3,3,8)
    plt.plot(t,n)
    plt.plot(t[i_PGV_max_n], n[i_PGV_max_n],"o")
    plt.text(t[i_PGV_max_n], n[i_PGV_max_n],f"{n[i_PGV_max_n]:.2f}")
    plt.plot(t[i_PGV_min_n], n[i_PGV_min_n],"o")
    plt.text(t[i_PGV_min_n], n[i_PGV_min_n],f"{n[i_PGV_min_n]:.2f}")
    plt.ylabel("$\\dot{n}$")
    plt.xlabel("t (s)")
    
    plt.subplot(3,3,3)
    plt.plot(t,az)
    plt.plot(t[i_PGA_max_z], az[i_PGA_max_z],"o")
    plt.text(t[i_PGA_max_z], az[i_PGA_max_z],f"{az[i_PGA_max_z]:.2f}")
    plt.plot(t[i_PGA_min_z], az[i_PGA_min_z],"o")
    plt.text(t[i_PGA_min_z], az[i_PGA_min_z],f"{az[i_PGA_min_z]:.2f}")
    plt.ylabel("$\\ddot{z}$")
    plt.title("PGA")
    plt.subplot(3,3,6)
    plt.plot(t,ae)
    plt.plot(t[i_PGA_max_e], ae[i_PGA_max_e],"o")
    plt.text(t[i_PGA_max_e], ae[i_PGA_max_e],f"{ae[i_PGA_max_e]:.2f}")
    plt.plot(t[i_PGA_min_e], ae[i_PGA_min_e],"o")
    plt.text(t[i_PGA_min_e], ae[i_PGA_min_e],f"{ae[i_PGA_min_e]:.2f}")
    plt.ylabel("$\\ddot{e}$")
    plt.subplot(3,3,9)
    plt.plot(t,an)
    plt.plot(t[i_PGA_max_n], an[i_PGA_max_n],"o")
    plt.text(t[i_PGA_max_n], an[i_PGA_max_n],f"{an[i_PGA_max_n]:.2f}")
    plt.plot(t[i_PGA_min_n], an[i_PGA_min_n],"o")
    plt.text(t[i_PGA_min_n], an[i_PGA_min_n],f"{an[i_PGA_min_n]:.2f}")
    plt.ylabel("$\\ddot{n}$")
    plt.xlabel("t (s)")
    
    plt.show()