#!/usr/bin/env python3
"""
Laboratorio No. 8 - Ejercicio 1 (inciso b)
Implementación en Python del programa del enunciado y medición de su tiempo
de ejecución con n = 1, 10, 100, 1 000, 10 000, 100 000 y 1 000 000.

Método de profiling:
  - timeit: mide el tiempo de la función repitiéndola las veces necesarias
    para que la medición sea confiable, y toma la mediana de varias tandas.
  - cProfile (opcional, con --cprofile N): muestra el perfil de llamadas y
    el tiempo acumulado de una ejecución con el n indicado.

Uso (desde la carpeta Lab8):
    python3 ejercicio-1/ejer1.py                  # mide todos los n (límite de 120 s por corrida)
    python3 ejercicio-1/ejer1.py --max-seg 3000   # permite corridas más largas (n = 100 000 tarda ~30 min)
    python3 ejercicio-1/ejer1.py --cprofile 1000  # muestra el perfil de cProfile para n = 1000

Genera en la carpeta ejercicio-1/: resultados_ej1.csv y grafica_ej1.png
"""
import argparse                  # Importa el módulo que lee las opciones enviadas por la terminal.
import cProfile                  # Importa el profiler de Python que cuenta llamadas y tiempos por función.
import csv                       # Importa el módulo que escribe archivos CSV.
import math                      # Importa funciones matemáticas como log2 y floor.
import os                        # Importa funciones para manejar rutas de archivos.
import pstats                    # Importa el módulo que da formato a los resultados de cProfile.
import statistics                # Importa funciones estadísticas como la mediana.
import time                      # Importa el reloj de alta precisión perf_counter.
import timeit                    # Importa el módulo estándar de Python para medir tiempos de ejecución.

import matplotlib                # Importa la librería de gráficas.
matplotlib.use("Agg")            # Indica que las gráficas se guardan en archivo sin abrir ventanas.
import matplotlib.pyplot as plt  # Importa la interfaz de matplotlib para dibujar.

CARPETA = os.path.dirname(os.path.abspath(__file__))  # Obtiene la carpeta donde está este archivo (ejercicio-1).
NS = [1, 10, 100, 1000, 10000, 100000, 1000000]       # Define los tamaños de input que pide el enunciado.


def function(n):                          # Implementa el algoritmo del enunciado y devuelve el contador.
    counter = 0                           # Inicializa el contador en 0.
    i = n // 2                            # Inicia i en n/2 (división entera, igual que en C).
    while i <= n:                         # Recorre i hasta n: ⌈n/2⌉ + 1 iteraciones.
        j = 1                             # Inicia j en 1 en cada vuelta del ciclo externo.
        while j + n // 2 <= n:            # Recorre j mientras j + n/2 <= n: ⌈n/2⌉ iteraciones.
            k = 1                         # Inicia k en 1 en cada vuelta del ciclo intermedio.
            while k <= n:                 # Recorre k mientras k <= n: ⌊log2 n⌋ + 1 iteraciones.
                counter += 1              # Incrementa el contador, que es la operación básica.
                k = k * 2                 # Duplica k, por eso este ciclo es logarítmico.
            j += 1                        # Avanza j de uno en uno.
        i += 1                            # Avanza i de uno en uno.
    return counter                        # Devuelve el total para compararlo con la fórmula del inciso a.


def operaciones_teoricas(n):              # Calcula con la fórmula del inciso a cuántas veces se ejecuta counter++.
    if n < 1:                             # Verifica si n es menor que 1.
        return 0                          # Devuelve 0 porque no hay iteraciones.
    externo = n - n // 2 + 1              # Calcula las iteraciones del ciclo externo (⌈n/2⌉ + 1).
    intermedio = n - n // 2               # Calcula las iteraciones del ciclo intermedio (⌈n/2⌉).
    interno = math.floor(math.log2(n)) + 1  # Calcula las iteraciones del ciclo interno (⌊log2 n⌋ + 1).
    return externo * intermedio * interno   # Devuelve el producto de los tres ciclos.


def medir(n):                                             # Mide el tiempo de una llamada a function(n) usando timeit.
    temporizador = timeit.Timer(lambda: function(n))      # Crea el temporizador que ejecuta la función con el n dado.
    veces, total = temporizador.autorange()               # Busca cuántas repeticiones hacen falta para medir al menos 0.2 s.
    if total / veces > 1.0:                               # Verifica si una sola llamada ya tarda más de un segundo.
        return total / veces, veces                       # Usa esa medición directamente para no repetir corridas largas.
    tandas = temporizador.repeat(repeat=5, number=veces)  # Repite la medición en 5 tandas de "veces" llamadas cada una.
    por_llamada = [t / veces for t in tandas]             # Convierte el tiempo de cada tanda a tiempo por llamada.
    return statistics.median(por_llamada), veces          # Devuelve la mediana y las repeticiones usadas.


def perfil_cprofile(n):                                   # Ejecuta cProfile sobre function(n) y muestra el perfil.
    perfil = cProfile.Profile()                           # Crea el objeto profiler.
    perfil.enable()                                       # Empieza a registrar llamadas y tiempos.
    resultado = function(n)                               # Ejecuta la función que se quiere perfilar.
    perfil.disable()                                      # Deja de registrar.
    print(f"cProfile de function({n}) -> contador = {resultado:,}")  # Muestra el resultado de la función.
    pstats.Stats(perfil).sort_stats("cumulative").print_stats(5)    # Imprime las 5 entradas con más tiempo acumulado.


def formato_tiempo(t):                                    # Convierte segundos a la unidad más legible.
    if t < 1e-3:                                          # Verifica si es menor a un milisegundo.
        return f"{t * 1e6:.3f} µs"                        # Lo devuelve en microsegundos.
    if t < 1:                                             # Verifica si es menor a un segundo.
        return f"{t * 1e3:.3f} ms"                        # Lo devuelve en milisegundos.
    if t < 3600:                                          # Verifica si es menor a una hora.
        return f"{t:.3f} s"                               # Lo devuelve en segundos.
    if t < 86400:                                         # Verifica si es menor a un día.
        return f"{t:,.0f} s (≈ {t / 3600:.1f} h)"         # Lo devuelve en segundos y horas.
    return f"{t:,.0f} s (≈ {t / 86400:.1f} días)"         # Lo devuelve en segundos y días.


def graficar(filas):                                      # Genera la gráfica de tamaño de input vs. tiempo.
    medidos = [f for f in filas if f["tipo"] == "medido"]     # Separa los puntos medidos.
    estimados = [f for f in filas if f["tipo"] == "estimado"]  # Separa los puntos estimados.
    ref = medidos[-1]                                     # Toma el último punto medido como referencia.
    teo = lambda x: x * x * max(1.0, math.log2(x))        # Define la curva teórica n² log n.
    c = ref["tiempo_s"] / teo(ref["n"])                   # Calcula la constante que ajusta la curva a ese punto.
    xs = [10 ** (k / 20) for k in range(121)]             # Genera valores de n entre 1 y 1 000 000.
    ys = [c * teo(x) for x in xs]                         # Calcula el tiempo teórico para cada valor.

    fig, ejes = plt.subplots(1, 2, figsize=(12, 4.6))     # Crea una figura con dos gráficas lado a lado.
    for ax, escala in zip(ejes, ["log", "lineal"]):       # Recorre la gráfica logarítmica y la lineal.
        ax.plot([f["n"] for f in medidos], [f["tiempo_s"] for f in medidos], "o-",
                color="#1f4e79", label="Tiempo medido")   # Dibuja los tiempos medidos.
        if estimados:                                     # Verifica si hay puntos estimados.
            ax.plot([f["n"] for f in estimados], [f["tiempo_s"] for f in estimados], "s--",
                    color="#c55a11", label="Tiempo estimado")  # Dibuja los tiempos estimados.
        ax.plot(xs, ys, ":", color="gray", label=r"Ajuste teórico $O(n^2 \log n)$")  # Dibuja la curva teórica.
        ax.set_xlabel("Tamaño de input n")                # Coloca el título del eje x.
        ax.set_ylabel("Tiempo (s)")                       # Coloca el título del eje y.
        ax.grid(True, which="both", alpha=0.3)            # Agrega una cuadrícula suave.
        if escala == "log":                               # Verifica si es la gráfica logarítmica.
            ax.set_xscale("log")                          # Pone el eje x en escala logarítmica.
            ax.set_yscale("log")                          # Pone el eje y en escala logarítmica.
            ax.set_title("Escala logarítmica")            # Coloca el título.
        else:                                             # Si es la gráfica lineal...
            ax.set_title("Escala lineal")                 # Coloca el título.
            ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))  # Muestra el eje x en notación científica.
        ax.legend(fontsize=8)                             # Agrega la leyenda.
    fig.suptitle("Ejercicio 1 (Python): tamaño de input vs. tiempo")  # Coloca el título general.
    fig.tight_layout()                                    # Ajusta los márgenes.
    fig.savefig(os.path.join(CARPETA, "grafica_ej1.png"), dpi=150)    # Guarda la gráfica como PNG.
    plt.close(fig)                                        # Cierra la figura para liberar memoria.


def main():                                               # Función principal del programa.
    ap = argparse.ArgumentParser()                        # Crea el lector de opciones de la terminal.
    ap.add_argument("--max-seg", type=float, default=120.0,
                    help="tiempo máximo estimado por corrida en segundos")  # Define el límite de tiempo por corrida.
    ap.add_argument("--cprofile", type=int, metavar="N",
                    help="solo muestra el perfil de cProfile para ese n")   # Define la opción para usar cProfile.
    args = ap.parse_args()                                # Lee las opciones enviadas.

    if args.cprofile is not None:                         # Verifica si se pidió el perfil de cProfile.
        perfil_cprofile(args.cprofile)                    # Muestra el perfil para el n indicado.
        return                                            # Termina sin hacer la medición completa.

    filas = []                                            # Inicializa la lista de resultados.
    costo_op = None                                       # Guarda los segundos por operación de la última medición.
    print(f"{'n':>9} | {'Operaciones':>17} | {'Tiempo':>22} | Tipo")  # Imprime el encabezado de la tabla.
    for n in NS:                                          # Recorre cada tamaño de input.
        ops = operaciones_teoricas(n)                     # Calcula cuántas operaciones debería hacer.
        if costo_op and costo_op * ops > args.max_seg:    # Verifica si la corrida tardaría más que el límite.
            t, tipo = costo_op * ops, "estimado"          # Estima el tiempo con el costo por operación medido.
        else:                                             # Si la corrida cabe en el límite...
            if n >= 1000:                                 # Verifica si n es lo bastante grande para validar la fórmula sin perder tiempo.
                assert function(n) == ops, "El contador no coincide con la fórmula"  # Comprueba el contador contra la fórmula.
            t, _ = medir(n)                               # Mide el tiempo por llamada con timeit.
            tipo = "medido"                               # Marca la fila como medida.
            if ops > 0:                                   # Verifica que haya operaciones para calcular el costo.
                costo_op = t / ops                        # Actualiza el costo por operación.
        filas.append({"n": n, "operaciones": ops, "tiempo_s": t, "tipo": tipo})  # Guarda la fila.
        print(f"{n:>9,} | {ops:>17,} | {formato_tiempo(t):>22} | {tipo}")       # Muestra la fila en la terminal.

    ruta_csv = os.path.join(CARPETA, "resultados_ej1.csv")    # Arma la ruta del CSV.
    with open(ruta_csv, "w", newline="") as f:                # Abre el CSV en modo escritura.
        w = csv.DictWriter(f, fieldnames=["n", "operaciones", "tiempo_s", "tipo"])  # Crea el escritor.
        w.writeheader()                                       # Escribe los encabezados.
        w.writerows(filas)                                    # Escribe todas las filas.
    graficar(filas)                                           # Genera la gráfica.
    print(f"\nResultados guardados en {ruta_csv} y grafica_ej1.png")  # Informa dónde quedaron los archivos.


if __name__ == "__main__":                                # Verifica que el archivo se ejecute directamente.
    main()                                                # Llama a la función principal.