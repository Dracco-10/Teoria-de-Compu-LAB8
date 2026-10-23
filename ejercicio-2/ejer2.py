#!/usr/bin/env python3
"""
Laboratorio No. 8 - Ejercicio 2 (inciso b)
Implementación en Python del programa del enunciado y medición de su tiempo
de ejecución con n = 1, 10, 100, 1 000, 10 000, 100 000 y 1 000 000.

Método de profiling:
  - timeit: mide el tiempo de la función repitiéndola las veces necesarias
    para que la medición sea confiable, y toma la mediana de varias tandas.
  - cProfile (opcional, con --cprofile N): muestra el perfil de llamadas; aquí
    se ve que print se llama exactamente n veces.

Durante la medición las impresiones se envían a /dev/null, porque escribir en
la terminal es mucho más lento que el algoritmo y arruinaría la medición.

Uso (desde la carpeta Lab8):
    python3 ejercicio-2/ejer2.py                  # mide todos los n
    python3 ejercicio-2/ejer2.py --demo 5         # ejecuta la función con n = 5 imprimiendo en pantalla
    python3 ejercicio-2/ejer2.py --cprofile 100000  # muestra el perfil de cProfile para n = 100 000

Genera en la carpeta ejercicio-2/: resultados_ej2.csv y grafica_ej2.png
"""
import argparse                  # Importa el módulo que lee las opciones enviadas por la terminal.
import contextlib                # Importa la herramienta para redirigir la salida estándar temporalmente.
import cProfile                  # Importa el profiler de Python que cuenta llamadas y tiempos por función.
import csv                       # Importa el módulo que escribe archivos CSV.
import os                        # Importa funciones para manejar rutas y el archivo /dev/null.
import pstats                    # Importa el módulo que da formato a los resultados de cProfile.
import statistics                # Importa funciones estadísticas como la mediana.
import timeit                    # Importa el módulo estándar de Python para medir tiempos de ejecución.

import matplotlib                # Importa la librería de gráficas.
matplotlib.use("Agg")            # Indica que las gráficas se guardan en archivo sin abrir ventanas.
import matplotlib.pyplot as plt  # Importa la interfaz de matplotlib para dibujar.

CARPETA = os.path.dirname(os.path.abspath(__file__))  # Obtiene la carpeta donde está este archivo (ejercicio-2).
NS = [1, 10, 100, 1000, 10000, 100000, 1000000]       # Define los tamaños de input que pide el enunciado.
impresiones = 0                                       # Cuenta cuántas veces se imprime "Sequence".


def function(n):                          # Implementa el algoritmo del enunciado.
    global impresiones                    # Indica que se va a modificar el contador global.
    if n <= 1:                            # Verifica si n es 1 o menor.
        return                            # Termina de inmediato sin imprimir nada.
    i = 1                                 # Inicia i en 1.
    while i <= n:                         # Recorre i hasta n: n iteraciones.
        j = 1                             # Inicia j en 1 en cada vuelta del ciclo externo.
        while j <= n:                     # Entra al ciclo interno.
            print("Sequence")             # Imprime el mensaje una vez.
            impresiones += 1              # Incrementa el contador de impresiones.
            break                         # Sale del ciclo interno, por lo que este solo da una vuelta.
        i += 1                            # Avanza i de uno en uno.


def impresiones_teoricas(n):              # Calcula con la fórmula del inciso a cuántas veces se imprime.
    return n if n > 1 else 0              # Devuelve n, o 0 si la función retorna de inmediato.


def contar(n):                                            # Cuenta las impresiones reales de una llamada a function(n).
    global impresiones                                    # Indica que se va a modificar el contador global.
    impresiones = 0                                       # Reinicia el contador.
    with open(os.devnull, "w") as nulo, contextlib.redirect_stdout(nulo):  # Envía las impresiones a /dev/null.
        function(n)                                       # Ejecuta la función una vez.
    return impresiones                                    # Devuelve cuántas impresiones hizo.


def medir(n):                                             # Mide el tiempo de una llamada a function(n) usando timeit.
    with open(os.devnull, "w") as nulo, contextlib.redirect_stdout(nulo):  # Envía las impresiones a /dev/null durante la medición.
        temporizador = timeit.Timer(lambda: function(n))  # Crea el temporizador que ejecuta la función con el n dado.
        veces, total = temporizador.autorange()           # Busca cuántas repeticiones hacen falta para medir al menos 0.2 s.
        tandas = temporizador.repeat(repeat=5, number=veces)  # Repite la medición en 5 tandas.
    por_llamada = [t / veces for t in tandas]             # Convierte el tiempo de cada tanda a tiempo por llamada.
    return statistics.median(por_llamada)                 # Devuelve la mediana del tiempo por llamada.


def perfil_cprofile(n):                                   # Ejecuta cProfile sobre function(n) y muestra el perfil.
    perfil = cProfile.Profile()                           # Crea el objeto profiler.
    with open(os.devnull, "w") as nulo, contextlib.redirect_stdout(nulo):  # Envía las impresiones a /dev/null.
        perfil.enable()                                   # Empieza a registrar llamadas y tiempos.
        function(n)                                       # Ejecuta la función que se quiere perfilar.
        perfil.disable()                                  # Deja de registrar.
    print(f"cProfile de function({n})")                   # Muestra qué se perfiló.
    pstats.Stats(perfil).sort_stats("cumulative").print_stats(5)  # Imprime las 5 entradas con más tiempo acumulado.


def formato_tiempo(t):                                    # Convierte segundos a la unidad más legible.
    if t < 1e-3:                                          # Verifica si es menor a un milisegundo.
        return f"{t * 1e6:.3f} µs"                        # Lo devuelve en microsegundos.
    if t < 1:                                             # Verifica si es menor a un segundo.
        return f"{t * 1e3:.3f} ms"                        # Lo devuelve en milisegundos.
    return f"{t:.3f} s"                                   # Lo devuelve en segundos.


def graficar(filas):                                      # Genera la gráfica de tamaño de input vs. tiempo.
    ref = filas[-1]                                       # Toma el punto con el n más grande como referencia.
    c = ref["tiempo_s"] / ref["n"]                        # Calcula la constante que ajusta la recta teórica c·n a ese punto.
    xs = [10 ** (k / 20) for k in range(121)]             # Genera valores de n entre 1 y 1 000 000.
    ys = [c * x for x in xs]                              # Calcula el tiempo teórico para cada valor.

    fig, ejes = plt.subplots(1, 2, figsize=(12, 4.6))     # Crea una figura con dos gráficas lado a lado.
    for ax, escala in zip(ejes, ["log", "lineal"]):       # Recorre la gráfica logarítmica y la lineal.
        ax.plot([f["n"] for f in filas], [f["tiempo_s"] for f in filas], "o-",
                color="#1f4e79", label="Tiempo medido")   # Dibuja los tiempos medidos.
        ax.plot(xs, ys, ":", color="gray", label=r"Ajuste teórico $O(n)$")  # Dibuja la recta teórica.
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
    fig.suptitle("Ejercicio 2 (Python): tamaño de input vs. tiempo")  # Coloca el título general.
    fig.tight_layout()                                    # Ajusta los márgenes.
    fig.savefig(os.path.join(CARPETA, "grafica_ej2.png"), dpi=150)    # Guarda la gráfica como PNG.
    plt.close(fig)                                        # Cierra la figura para liberar memoria.


def main():                                               # Función principal del programa.
    ap = argparse.ArgumentParser()                        # Crea el lector de opciones de la terminal.
    ap.add_argument("--demo", type=int, metavar="N",
                    help="ejecuta la función con ese n imprimiendo en pantalla")  # Define la opción de demostración.
    ap.add_argument("--cprofile", type=int, metavar="N",
                    help="solo muestra el perfil de cProfile para ese n")        # Define la opción para usar cProfile.
    args = ap.parse_args()                                # Lee las opciones enviadas.

    if args.demo is not None:                             # Verifica si se pidió la demostración.
        function(args.demo)                               # Ejecuta la función imprimiendo en la terminal.
        print(f"-> impresiones: {impresiones}")           # Muestra cuántas veces imprimió.
        return                                            # Termina sin hacer la medición completa.
    if args.cprofile is not None:                         # Verifica si se pidió el perfil de cProfile.
        perfil_cprofile(args.cprofile)                    # Muestra el perfil para el n indicado.
        return                                            # Termina sin hacer la medición completa.

    filas = []                                            # Inicializa la lista de resultados.
    print(f"{'n':>9} | {'Impresiones':>11} | {'Tiempo':>12} | Tipo")  # Imprime el encabezado de la tabla.
    for n in NS:                                          # Recorre cada tamaño de input.
        imp = contar(n)                                   # Cuenta las impresiones reales de la función.
        assert imp == impresiones_teoricas(n), "Las impresiones no coinciden con la fórmula"  # Comprueba contra la fórmula.
        t = medir(n)                                      # Mide el tiempo por llamada con timeit.
        filas.append({"n": n, "impresiones": imp, "tiempo_s": t, "tipo": "medido"})  # Guarda la fila.
        print(f"{n:>9,} | {imp:>11,} | {formato_tiempo(t):>12} | medido")           # Muestra la fila en la terminal.

    ruta_csv = os.path.join(CARPETA, "resultados_ej2.csv")    # Arma la ruta del CSV.
    with open(ruta_csv, "w", newline="") as f:                # Abre el CSV en modo escritura.
        w = csv.DictWriter(f, fieldnames=["n", "impresiones", "tiempo_s", "tipo"])  # Crea el escritor.
        w.writeheader()                                       # Escribe los encabezados.
        w.writerows(filas)                                    # Escribe todas las filas.
    graficar(filas)                                           # Genera la gráfica.
    print(f"\nResultados guardados en {ruta_csv} y grafica_ej2.png")  # Informa dónde quedaron los archivos.


if __name__ == "__main__":                                # Verifica que el archivo se ejecute directamente.
    main()                                                # Llama a la función principal.