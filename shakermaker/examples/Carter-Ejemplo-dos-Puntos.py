from shakermaker.shakermaker import ShakerMaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource 
from shakermaker.faultsource import FaultSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.tools.plotting import ZENTPlot
from scipy.integrate import cumulative_trapezoid

# Inicializar modelo de corteza de dos capas
corteza = CrustModel(2)

# Capa lenta
Vp=4.000           # Velocidad de la onda P (km/s)
Vs=2.000           # Velocidad de la onda S (km/s)
rho=2.600          # Densidad (gm/cm**3)
Qp=10000.          # Factor Q para la onda P
Qs=10000.          # Factor Q para la onda S
espesor = 1.0      # Auto-explicativo
corteza.add_layer(espesor, Vp, Vs, rho, Qp, Qs)

# Semi espacio
Vp=6.000
Vs=3.464
rho=2.700
Qp=10000.
Qs=10000.
espesor = 0      # Espesor cero --> semi espacio
corteza.add_layer(espesor, Vp, Vs, rho, Qp, Qs)

# Inicializar Fuentes
fuente1 = PointSource([0,0,4], [90,90,0])
fuente2 = PointSource([7,15,4], [90,90,0])
falla = FaultSource([fuente1, fuente2], metadata={"name":"fuentes_dobles"})

# Inicializar Receptores
estacion1 = Station([0,4,0], metadata={"name":"Estación1"})
estacion2 = Station([7,19,0], metadata={"name":"Estación2"})
estaciones = StationList([estacion1, estacion2], metadata={"name":"lista_estaciones"})

modelo = ShakerMaker(corteza, falla, estaciones)
modelo.run(
    dt=0.005,   # Output time-step
    nfft=2048,  # N timesteps
    dk=0.1,     # wavenumber discretization
    tb=20       # Initial zero-padding
)


def compute_and_compare_integral(estacion):
    # Extraer datos directamente del objeto Estación usando get_response()
    z, e, n, t = estacion.get_response()

    # Calcular la velocidad manualmente integrando la aceleración
    v_integral_e = cumulative_trapezoid(e, t, initial=0)
    v_integral_n = cumulative_trapezoid(n, t, initial=0)
    v_integral_z = cumulative_trapezoid(z, t, initial=0)

    # Calcular el desplazamiento manualmente integrando la velocidad calculada manualmente
    d_integral_e = cumulative_trapezoid(v_integral_e, t, initial=0)
    d_integral_n = cumulative_trapezoid(v_integral_n, t, initial=0)
    d_integral_z = cumulative_trapezoid(v_integral_z, t, initial=0)

    # Imprimir los valores integrados finales para comparación
    print(f"Resultados para {estacion.metadata['name']}")
    print("--------------------------------------")
    print(f"Velocidad (E): Integral Manual: {v_integral_e[-1]:.4f}")
    print(f"Velocidad (N): Integral Manual: {v_integral_n[-1]:.4f}")
    print(f"Velocidad (Z): Integral Manual: {v_integral_z[-1]:.4f}")
    print(f"Desplazamiento (E): Integral Manual: {d_integral_e[-1]:.4f}")
    print(f"Desplazamiento (N): Integral Manual: {d_integral_n[-1]:.4f}")
    print(f"Desplazamiento (Z): Integral Manual: {d_integral_z[-1]:.4f}")
    print("\n")

# Calcular y comparar para ambas estaciones
compute_and_compare_integral(estacion1)
compute_and_compare_integral(estacion2)

# Visualizar resultados para ambas estaciones
ZENTPlot(estacion1, xlim=[0,60], show=True)
ZENTPlot(estacion2, xlim=[0,60], show=True)
