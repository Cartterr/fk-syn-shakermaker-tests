import subprocess
import os
import matplotlib.pyplot as plt
import obspy
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d
from shakermaker import shakermaker
from shakermaker.crustmodel import CrustModel
from shakermaker.pointsource import PointSource
from shakermaker.station import Station
from shakermaker.stationlist import StationList
from shakermaker.faultsource import FaultSource
from multiprocessing import Process, Manager
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider




#Establecer las rutas del directorio
fk_syn_dir = "./fk-syn"

def run_fortran_scripts(nfft_fortran, dt_fortran, dk_fortran, tb_fortran, sigma_fortran, kc_fortran, pmin_fortran, pmax_fortran, taper_fortran):
    #Definir los parámetros del modelo (asumiendo un modelo predeterminado "hk" y una profundidad "15")
    model = "hk"
    depth = "15"  #Actualice esto según la profundidad del modelo.
    fk_model_params = f"{model}/{depth}/k"  #El '/k' supone que se utiliza la relación vp/vs; eliminar si se utiliza vp real
    #Defina las distancias (reemplácelas con distancias reales según sea necesario)
    #distancias = " ".join([str(d) for d in range(5, 85, 5)]) # Ejemplo: "5 10 15 ... 80"
    distances = 50



    #No se proporciona el parámetro algo; debe determinarse según sus requisitos
    smth_fortran = 1  #Valor de ejemplo, debe ser 2^n
    #Construya el comando FK con los valores del control deslizante
    #fk_command = f"./fk.pl -M{fk_model_params} -N{nfft_fortran}/{dt_fortran}/{smth_fortran}/{dk_fortran}/{taper_fortran} -P{pmin_fortran}/{pmax_fortran}/{kc_fortran} -S2 -R0 -H0/0 -D -U0 -Xcmd {distancias}"
    fk_command = f"./fk.pl -M{fk_model_params} -N{nfft_fortran}/{dt_fortran}/{smth_fortran}/{dk_fortran}/{taper_fortran} -P{pmin_fortran}/{pmax_fortran}/{kc_fortran} -S2 -R0 -H0/0 -D -U0 {distances}"
    print(fk_command)
    subprocess.run(fk_command, shell=True, cwd=fk_syn_dir)
    print(f"./fk.pl -Mhk/15/k -N{nfft_fortran}/{dt_fortran}/1/{dk_fortran}/0.3 -P0/1/15 -S2 50")
    subprocess.run(f"./fk.pl -Mhk/15/k -N{nfft_fortran}/{dt_fortran}/1/{dk_fortran}/0.3 -P0/1/15 -S2 50", shell=True, cwd=fk_syn_dir)

    #Cree el comando SYN con los valores del control deslizante (actualice magnitud, rumbo, inclinación, inclinación según sea necesario)
    magnitude = "4.5"  #Magnitud de ejemplo
    strike = "0"     #Huelga de ejemplo
    dip = "80"         #Ejemplo de inmersión
    rake = "0"       #rastrillo de ejemplo
    azimuth = "33.5"   #Ejemplo de azimut
    syn_model_params = f"{model}_{depth}"
    syn_command = f"./syn -M{magnitude}/{strike}/{dip}/{rake} -D1 -A{azimuth} -OPAS.z -G{syn_model_params}/50.grn.0"
    
    print(syn_command)
    subprocess.run(syn_command, shell=True, cwd=fk_syn_dir)
    print("./syn -M4.5/355/80/-70 -D1 -A33.5 -OPAS.z -Ghk_15/50.grn.0")
    subprocess.run(f"./syn -M4.5/355/80/-70 -D1 -A33.5 -OPAS.z -Ghk_15/50_0.grn.0", shell=True, cwd=fk_syn_dir)


def visualize_sac(filename, ax, scaling_factor=1, num_points=1000):
    #Genere la ruta completa al archivo SAC
    full_path = os.path.join(fk_syn_dir, filename)

    #Leer archivo SAC
    st = obspy.read(full_path)
    data = st[0].data * scaling_factor
    times = st[0].times()

    # Interpolation for smoother lines
    interp_func = interp1d(times, data, kind='cubic')
    high_res_times = np.linspace(times.min(), times.max(), num_points)
    high_res_data = interp_func(high_res_times)

    ax.plot(high_res_times, high_res_data, label=f'{filename}')



def run_shmk(nfft_test, dt_test, dk_test, tb, sigma, kc, pmin, pmax, taper, results):
    #Definir un modelo de corteza de dos capas donde la segunda capa es un medio espacio infinito
    crust = CrustModel(2)  #Inicializar con 2 capas
    #Agregue la primera capa con espesor finito.
    crust.add_layer(
        d=15.0,    #Espesor en km
        vp=6.0,    #Velocidad de la onda P (km/s)
        vs=3.5,    #Velocidad de onda S (km/s)
        rho=2.8,   #Densidad (g/cm^3)
        qp=2000,   #Factor Q para la onda P
        qs=1000    #Factor Q para onda S
    )
    #Agregar segunda capa (medio espacio)
    crust.add_layer(
        d=0.0,     #Espesor en km, 0 para medio espacio
        vp=6.0,    #Velocidad de la onda P (km/s)
        vs=3.5,    #Velocidad de onda S (km/s)
        rho=2.8,   #Densidad (g/cm^3)
        qp=2000,   #Factor Q para la onda P
        qs=1000    #Factor Q para onda S
    )

    #Crear una fuente puntual simple
    strike, dip, rake = 0, 80, 0  #Ángulos de orientación de la fuente
    source_depth = 15  #Profundidad de la fuente en km
    source = PointSource([0, 0, source_depth], [strike, dip, rake])
    fault = FaultSource([source], metadata={"name": "simple-point-source"})

    #Crear una única estación a una distancia específica
    station_distance = 50  #Distancia en km
    station = Station([station_distance, 0, 0], metadata={"name": "simple-station"})
    stations = StationList([station], metadata={"name": "station_list"})

    #Ejecute la simulación con ShakerMaker
    shaker = shakermaker.ShakerMaker(crust, fault, stations)
    shaker.run(
        dt=dt_test,          #Paso de tiempo de salida
        nfft=nfft_test,      #Número de pasos de tiempo (longitud FFT)
        dk=dk_test,          #Discretización del número de onda
        tb=tb,               #Relleno de ceros inicial
        sigma=sigma,             #Tasa de amortiguación
        kc=kc,             #Número de onda máximo
        pmin=pmin,              #Mín. lentitud (1/Vs) para el máx. velocidad de fase
        pmax=pmax,              #Máx. lentitud (1/Vs) para el min. velocidad de fase
        taper=taper            #Cono del filtro de paso bajo
    )

    #Recuperar y almacenar los resultados.
    z, e, n, t = station.get_response()
    results.extend([z, e, n, t, [station_distance], stations])






        

#Una función para actualizar el gráfico según los valores del control deslizante.
def update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, 
           s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, 
           s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, 
           s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax):   
    ax.clear()

    #Obtenga los valores actuales de los controles deslizantes de límite del eje x
    xmin_val = s_xmin.val
    xmax_val = s_xmax.val
    
    #Establezca los límites del eje x según los valores del control deslizante
    ax.set_xlim([xmin_val, xmax_val])
    
    #Recuperar valores del control deslizante para Fortran
    nfft_fortran = s_nfft_fortran.val
    dt_fortran = s_dt_fortran.val
    dk_fortran = s_dk_fortran.val
    sigma_fortran = s_sigma_fortran.val
    kc_fortran = s_kc_fortran.val
    pmin_fortran = s_pmin_fortran.val
    pmax_fortran = s_pmax_fortran.val
    taper_fortran = s_taper_fortran.val
    fk_syn_scale = s_fk_syn_scale.val

    #Recuperar valores del control deslizante para Shakermaker
    nfft_shmk = s_nfft_shmk.val
    dt_shmk = s_dt_shmk.val
    dk_shmk = s_dk_shmk.val
    tb = s_tb_shmk.val
    sigma_shmk = s_sigma_shmk.val
    kc_shmk = s_kc_shmk.val
    pmin_shmk = s_pmin_shmk.val
    pmax_shmk = s_pmax_shmk.val
    taper_shmk = s_taper_shmk.val
    
    #Vuelva a ejecutar las simulaciones de Fortran con nuevos parámetros.
    run_fortran_scripts(nfft_fortran, dt_fortran, dk_fortran, tb, sigma_fortran, kc_fortran, pmin_fortran, pmax_fortran, taper_fortran)
    
    #Trazar los resultados de los scripts de Fortran
    seismic_components = ["e"]
    fk_syn_scale = s_fk_syn_scale.val
    for component in seismic_components:
        visualize_sac(f"PAS.{component}", ax, fk_syn_scale)
        #aprobar
    #Vuelva a ejecutar las simulaciones de Shakermaker con nuevos parámetros.
    manager = Manager()
    results = manager.list()
    process = Process(target=run_shmk, args=(nfft_shmk, dt_shmk, dk_shmk, tb, sigma_shmk, kc_shmk, pmin_shmk, pmax_shmk, taper_shmk, results))
    process.start()
    process.join(timeout=1)

    if process.is_alive():
        print("Timed out. Moving to the next nfft.")
        process.terminate()
        process.join()

    #Recuperar los resultados
    z, e, n, t, distances_km, stations = results
    
    for i, station in enumerate(stations):
        for component in seismic_components:
            if component == "z":
                ax.plot(t, z, label=f'Shakermaker Z at {distances_km[i]} km and nfft={nfft_shmk}')
            elif component == "e":
                ax.plot(t, e, label=f'Shakermaker E at {distances_km[i]} km and nfft={nfft_shmk}')
            elif component == "n":
                ax.plot(t, n, label=f'Shakermaker N at {distances_km[i]} km and nfft={nfft_shmk}')
    
    #Finalizar la trama combinada.
    ax.legend()
    ax.set_title(f"Gráfico de Componente(s) '{', '.join(seismic_components)}'")

    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud (km)")
    
    fig.canvas.draw_idle()





#Tu función principal
def main():
    #Crea la primera trama
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.canvas.manager.window.wm_geometry("+2840+0")  #Posición en la esquina superior izquierda
    ax.set_title("Output Gráficos")

    #Trazar algo en la primera figura.
    #ax.plot([0, 1], [0, 1])
    #Crea la segunda figura para controles deslizantes.
    shakermaker_slider_fig = plt.figure(figsize=(9, 4))
    shakermaker_slider_fig.canvas.manager.window.wm_geometry("+1920+0")  #Posición a la derecha
    shakermaker_slider_fig.suptitle('Shakermaker Slider')  #Añade un título a la figura.

    fortran_slider_fig = plt.figure(figsize=(9, 4))
    fortran_slider_fig.canvas.manager.window.wm_geometry("+1920+540")  #Posición a la derecha
    fortran_slider_fig.suptitle('Fortran Slider')  #Añade un título a la figura.
    #Crear controles deslizantes con nueva disposición
    fortran_color = '#FF6347'  #Hex para un tomate rojo
    shakermaker_color = '#2E8B57'  #Hex para un verde mar
    #Definir el punto de partida y el tamaño del paso vertical para los controles deslizantes.
    vertical_start = 0.9
    vertical_step = 0.07

    #Definir controles deslizantes para la configuración de Fortran
    ax_nfft_fortran = fortran_slider_fig.add_axes([0.1, vertical_start, 0.8, 0.05], facecolor=fortran_color)
    ax_dt_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_dk_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 2 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_sigma_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 3 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_kc_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 4 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_pmin_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 5 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_pmax_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 6 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_taper_fortran = fortran_slider_fig.add_axes([0.1, vertical_start - 7 * vertical_step, 0.8, 0.05], facecolor=fortran_color)
    ax_fk_syn_scale = fortran_slider_fig.add_axes([0.1, vertical_start - 8 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    

    #Definir controles deslizantes para la configuración de Shakermaker
    ax_nfft_shmk = shakermaker_slider_fig.add_axes([0.1, vertical_start, 0.8, 0.05], facecolor=shakermaker_color)
    ax_dt_shmk = shakermaker_slider_fig.add_axes([0.1, vertical_start - vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_dk_shmk = shakermaker_slider_fig.add_axes([0.1, vertical_start - 2 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_tb = shakermaker_slider_fig.add_axes([0.1, vertical_start - 3 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_sigma = shakermaker_slider_fig.add_axes([0.1, vertical_start - 4 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_kc = shakermaker_slider_fig.add_axes([0.1, vertical_start - 5 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_pmin = shakermaker_slider_fig.add_axes([0.1, vertical_start - 6 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_pmax = shakermaker_slider_fig.add_axes([0.1, vertical_start - 7 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_taper = shakermaker_slider_fig.add_axes([0.1, vertical_start - 8 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)


    s_nfft_shmk = Slider(ax_nfft_shmk, 'NFFT', valmin=64, valmax=1024, valinit=512, valstep=[64, 128, 256, 512, 1024])
    s_dt_shmk = Slider(ax_dt_shmk, 'dt', 0.001, 0.999, valinit=0.091)
    s_dk_shmk = Slider(ax_dk_shmk, 'dk', 40, 42, valinit=41.43)
    s_tb_shmk = Slider(ax_tb, 'tb', 1, 2.2, valinit=2.1)
    s_sigma_shmk = Slider(ax_sigma, 'Sigma', 1.8, 2.1, valinit=1.97)
    s_kc_shmk = Slider(ax_kc, 'kc', 0.001, 90, valinit=53.86)
    s_pmin_shmk = Slider(ax_pmin, 'Pmin', 0, 2, valinit=0.008)
    s_pmax_shmk = Slider(ax_pmax, 'Pmax', 0, 2, valinit=0.498)
    s_taper_shmk = Slider(ax_taper, 'Taper', 0.01, 1, valinit=0.9931)

    s_nfft_fortran = Slider(ax_nfft_fortran, 'NFFT', valmin=64, valmax=1024, valinit=512, valstep=[64, 128, 256, 512, 1024])
    s_dt_fortran = Slider(ax_dt_fortran, 'dt',  0.0, 0.6, valinit=0.2408)
    s_dk_fortran = Slider(ax_dk_fortran, 'dk', 0.2302, 0.2306, valinit=0.2304056)
    s_sigma_fortran = Slider(ax_sigma_fortran, 'Sigma', 0, 20, valinit=9.58)
    s_kc_fortran = Slider(ax_kc_fortran, 'kc Kappa', 0.001, 90, valinit=13.18)
    s_pmin_fortran = Slider(ax_pmin_fortran, 'Pmin', 0, 2, valinit=0)
    s_pmax_fortran = Slider(ax_pmax_fortran, 'Pmax', 0, 2, valinit=1.292)
    s_taper_fortran = Slider(ax_taper_fortran, 'Taper', 0.01, 1, valinit=0.999)
    s_fk_syn_scale = Slider(ax_fk_syn_scale, 'scale', valmin=1e10, valmax=1e20, valinit=0.1403e20)
    


    #Controles deslizantes mínimo-máximo
    ax_xmin = shakermaker_slider_fig.add_axes([0.1, vertical_start - 9 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)
    ax_xmax = shakermaker_slider_fig.add_axes([0.1, vertical_start - 10 * vertical_step, 0.8, 0.05], facecolor=shakermaker_color)

    s_xmin = Slider(ax_xmin, 'Xmin', valmin=-10, valmax=200, valinit=15)
    s_xmax = Slider(ax_xmax, 'Xmax', valmin=-10, valmax=200, valinit=60)

    #Modifique los controladores de eventos 'on_changed' para incluir todos los controles deslizantes y los parámetros de la función de actualización
    s_nfft_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_dt_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_dk_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_sigma_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_kc_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_pmin_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_pmax_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_taper_fortran.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_fk_syn_scale.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))


    s_nfft_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_dt_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_dk_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_tb_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_sigma_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_kc_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_pmin_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_pmax_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))
    s_taper_shmk.on_changed(lambda val: update(val, s_nfft_fortran, s_dt_fortran, s_dk_fortran, s_sigma_fortran, s_kc_fortran, s_pmin_fortran, s_pmax_fortran, s_taper_fortran, s_fk_syn_scale, s_nfft_shmk, s_dt_shmk, s_dk_shmk, s_tb_shmk, s_sigma_shmk, s_kc_shmk, s_pmin_shmk, s_pmax_shmk, s_taper_shmk, ax, fig, s_xmin, s_xmax))


    #Mostrar la trama con controles deslizantes
    plt.show()


if __name__ == "__main__":
    main()