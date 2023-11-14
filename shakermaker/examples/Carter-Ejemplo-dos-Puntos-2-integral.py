from scipy.integrate import cumulative_trapezoid
from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.faultsource import FaultSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.tools.plotting import ZENTPlot
from shakermaker.stf_extensions import Brune
from shakermaker.sl_extensions import DRMBox
import numpy as np

# Geometría del mecanismo de falla
ϕ, θ, λ = 0., 90., 0.    # Ángulos de strike, inclinación y deslizamiento

# Función del tiempo de la fuente
t0, f0 = 0., 2.                 # Tiempo pico y frecuencia de esquina
stf = Brune(f0=f0, t0=t0)

# Crear dos fuentes posicionadas razonablemente separadas y lejos de la caja DRM
fuente1 = PointSource([-5, -5, 1], [ϕ, θ, λ], tt=0, stf=stf)
fuente2 = PointSource([15, 25, 1], [ϕ, θ, λ], tt=0, stf=stf)
falla = FaultSource([fuente1, fuente2], metadata={"name": "fuentes_dobles"})

# Crear modelo de corteza (similar al ejemplo 1)
vp, vs, rho, Qa, Qb = 6.000, 3.500, 2.700, 10000., 10000.
corteza = CrustModel(1)
espesor = 0
corteza.add_layer(espesor, vp, vs, rho, Qa, Qb)

# Diseñar una caja DRM para una frecuencia máxima fmax
fmax = 10.  # Hz
dx = vs / fmax / 15

# Especificación de la Caja DRM (plano de 10x20 km)
nx, ny, nz = 10, 20, 4
x0 = [5, 10, 0]
caja_drm = DRMBox(x0, [nx, ny, nz], [dx, dx, dx], metadata={"name": "plano_drm"})

# Crear dos estaciones de registro dentro del plano de 10x20 km
s1 = Station([5, 10, 0], metadata={"name": "Estación1", "filter_results": False, "filter_parameters": {"fmax": 10.}})
s2 = Station([5, 20, 0], metadata={"name": "Estación2", "filter_results": False, "filter_parameters": {"fmax": 10.}})
estaciones = StationList([s1, s2], metadata={"name": "lista_estaciones"})

# Crear modelo, configurar parámetros y ejecutar
modelo = shakermaker.ShakerMaker(corteza, falla, estaciones)
modelo.run(dt=0.005, nfft=2048, dk=0.1, tb=20)

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

# Visualizar resultados para ambas estaciones
compute_and_compare_integral(s1)
ZENTPlot(s1, show=True)
compute_and_compare_integral(s2)
ZENTPlot(s2, show=True)
