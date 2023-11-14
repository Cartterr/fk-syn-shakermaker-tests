from shakermaker import shakermaker
from shakermaker.station import Station
from shakermaker.tools.plotting import ZENTPlot,cumulative_trapezoid
from fuctions import piece_wise_linear2 as pwl
from normspectrum import Espectro433
import numpy as np
import matplotlib.pylab as plt


nu = 0.05
tmax = 50.
dt = np.linspace(0,1.,2000)
w = np.zeros(len(dt))

for i in range(len(dt)):
    if dt[i] != 0:    
        w[i] = 2*np.pi/dt[i]

S = 0.9
To = 0.15 #[s]
p = 2
Ao = 0.3 *9.81 
I = 1.2
R = 1

T,Sah_433,Sav_433 = Espectro433(S,Ao,R,I,To,p)

legend = []
files = [
    "resultado_s0.npz",
    "resultado_s1.npz",
    "resultado_s2.npz",
    "resultado_s3.npz",
    "resultado_s4.npz",
    "resultado_s5.npz",
    "resultado_s6.npz",
    "resultado_s7.npz",
    "resultado_s8.npz",
    "resultado_s9.npz"]

#PLOTEO PSEUDO ESPECTRO Z
plt.figure(figsize=(9, 5.5))
for i in range(len(files)):
    legend.append(files[i])
    s = Station()
    s.load(files[i])

    z,e,n,t = s.get_response()
    z = z[t<tmax] 
    t = t[t<tmax]

    az = np.gradient(z,t).tolist()
    Spaz = []

    for j in range(len(w)):
        wi = w[j]
        u_z,v_z = pwl(az,wi,nu)
        Saz = max(max(u_z),(abs(min(u_z))))*wi**2
        Spaz.append(Saz)

    plt.plot(dt,Spaz,'-')

legend.append('NCh433')
plt.plot(dt, Sav_433,'k--')
plt.title('Pseudoespectros Spa Vertical')
plt.xlabel('Periodo T [s]')
plt.ylabel('Aceleración [m/s/s]')
plt.legend(legend)
plt.grid()
plt.savefig('SpaVertical.png')
plt.show()
plt.figure(figsize=(9, 5.5))
#PLOTEO PSEUDO ESPECTRO ESTE
for i in range(len(files)):
    s = Station()
    s.load(files[i])
    z,e,n,t = s.get_response()
    e = e[t<tmax]
    t = t[t<tmax]
    ae = np.gradient(e,t).tolist()
    Spe = []

    for j in range(len(w)):
        wi = w[j]
        u_x,v_x = pwl(ae,wi,nu)
        Sae = max(max(u_x),(abs(min(u_x))))*wi**2
        Spe.append(Sae)
    plt.plot(dt,Spe,'-')

plt.plot(dt,Sah_433,'k--')
plt.title('Pseudoespectros Spa Este')
plt.xlabel('Periodo T [s]')
plt.ylabel('Aceleración [m/s/s]')
plt.legend(legend)
plt.grid()
plt.savefig('SpaEste.png')
plt.show()
plt.figure(figsize=(9, 5.5))
#PLOTEO PSEUDO ESPECTRO NORTE
for i in range(len(files)):
    s = Station()
    s.load(files[i])
    z,e,n,t = s.get_response()
    n = n[t<tmax]
    t = t[t<tmax]
    an = np.gradient(n,t).tolist()
    Spn = []

    for j in range(len(w)):
        wi = w[j]
        u_y,v_y = pwl(an,wi,nu)
        San = max(max(u_y),(abs(min(u_y))))*wi**2
        Spn.append(San)
    plt.plot(dt,Spn,'-')
plt.plot(dt,Sah_433,'k--')
plt.title('Pseudoespectros Spa Norte')
plt.xlabel('Periodo T [s]')
plt.ylabel('Aceleración [m/s/s]')
plt.legend(legend)
plt.grid()
plt.savefig('SpaNorte.png')
plt.show()


