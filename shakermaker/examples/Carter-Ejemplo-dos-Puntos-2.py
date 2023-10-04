from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.faultsource import FaultSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.tools.plotting import ZENTPlot
from shakermaker.stf_extensions import Brune
from shakermaker.sl_extensions import DRMBox

# Geometría del mecanismo de falla
ϕ, θ, λ = 0., 90., 0.    # Ángulos de strike, inclinación y deslizamiento

# Función de Tiempo de la Fuente
t0, f0 = 0., 2.                 # Tiempo pico y frecuencia de esquina
stf = Brune(f0=f0, t0=t0)

# Crear dos fuentes posicionadas razonablemente separadas y lejos de la caja DRM
fuente1 = PointSource([-5, -5, 1], [ϕ, θ, λ], tt=0, stf=stf)
fuente2 = PointSource([15, 25, 1], [ϕ, θ, λ], tt=0, stf=stf)
falla = FaultSource([fuente1, fuente2], metadata={"name": "dual_sources"})

# Crear modelo de corteza (similar al ejemplo1)
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
caja_drm = DRMBox(x0, [nx, ny, nz], [dx, dx, dx], metadata={"name": "drm_plane"})

# Crear dos estaciones de registro dentro del plano de 10x20 km
s1 = Station([5, 10, 0], metadata={"name": "Estación1", "filter_results": False, "filter_parameters": {"fmax": 10.}})
s2 = Station([5, 20, 0], metadata={"name": "Estación2", "filter_results": False, "filter_parameters": {"fmax": 10.}})
estaciones = StationList([s1, s2], metadata={"name": "estaciones_drm"})

# Crear modelo, configurar parámetros y ejecutar
modelo = shakermaker.ShakerMaker(corteza, falla, estaciones)
modelo.run(dt=0.005, nfft=2048, dk=0.1, tb=20)

# Visualizar resultados para ambas estaciones
ZENTPlot(s1, show=True)
ZENTPlot(s2, show=True)
