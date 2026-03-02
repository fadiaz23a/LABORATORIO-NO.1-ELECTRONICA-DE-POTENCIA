import serial # comunicacion serial con el ESP32
import matplotlib.pyplot as plt # graficar señales
import numpy as np # operaciones matematicas con vectores
from math import sqrt, cos, sin, pi , acos# funciones matematicas

############################ CONFIGURACION #################################
N = 200 # NUMERO DE MUESTRAS POR PERIODO DE LA SEÑAL
f_senal = 60 # Frecuencia de la señal muestreada
num_muestras_i=0 # Numero de muestras de corriente antes de su valor pico
num_muestras_v=0 # Numero de muestras de voltaje antes de su valor pico
ADC_VOLT=220 # Valor medio de ADC del pin que recibe la señal de Voltaje
ADC_CORR=242 # Valor medio de ADC del pin que recibe la señal de Corriente
CORRIENTE_PICO=0.34 # Corriente maxima medida en el montaje real 
VOLTAJE_PICO=170 # Voltaje maximo medido en el montaje real
ser = serial.Serial('COM3', 115200, timeout=5) # comunicacion serial con ESP32 
#                                                serial.Serial('puerto COM usado', velocidad de comunicación,tiempo limite de espera)

print("Esperando datos...") # mensaje mostrado en consola mientras recibe datos desde el ESP32

plt.ion()  # permite actualizar graficas sin bloquear el codigo

while True: # Loop principal del programa
    
    volt_data = [] # Vector de datos de voltaje
    corr_data = [] # Vector de datos de corriente

    # Esperar START
    while True:
        linea = ser.readline().decode().strip() # leer linea del puerto serial
        if linea == "START":
            break  # ESP32 empezo a enviar datos

    # Leer datos
    while True:
        linea = ser.readline().decode().strip() # leer linea del puerto serial
        if linea == "END":
            break # ESP32 termino de enviar los datos
        if "," in linea: # verificar que la linea tiene datos validos
            v, c = linea.split(",") # separar voltaje y corriente
            volt_data.append(int(v))  # agregar datos de voltaje al vector
            corr_data.append(int(c))  # agregar datos de corriente al vector


    # Verificar que se recibieron exactamente N muestras
    if len(volt_data) != N:
        print("Error en cantidad de muestras") # mostrar mensaje si no hay N muestras
        continue

    # --- CONVERTIR A REAL --- #
    voltajes_reales = [] # vectores de datos procesados de voltaje
    corrientes_reales = [] # vectores de datos procesados de corriente

    suma_v2 = 0 # sumador de los datos de voltaje  al cuadrado para calculo de RMS
    suma_i2 = 0 # sumador de los datos de corriente al cuadrado para calculo de RMS
    suma_vi = 0 # sumador de producto voltaje*corriente para calcular angulo de desfase

    ####### Ciclo de procesamiento de datos ########
    for i in range(N):
        muestra_v = volt_data[i] # traspasar dato del vector de voltaje a muestra_v para realizar conversion dato por dato
        muestra_i = corr_data[i] # traspasar dato del vector de corriente a muestra_i para realizar conversion dato por dato

        # convertir datos del ADC a voltaje real
        # Restar offset y escalar cada dato con respecto a los valores reales
        v_real = (muestra_v - ADC_VOLT) * (VOLTAJE_PICO / ADC_VOLT)
        # convertir datos del ADC a corriente real
        # Restar offset y escalar cada dato con respecto a los valores reales
        i_real = (muestra_i - ADC_CORR) * (CORRIENTE_PICO / ADC_CORR) 


        voltajes_reales.append(v_real) # Vector que guarda los datos de voltaje procesados
        corrientes_reales.append(i_real) # Vector que guarda los datos de corriente procesados

        suma_v2 += v_real * v_real #sumador de voltaje al cuadrado
        suma_i2 += i_real * i_real #sumador de corriente al cuadrado
        suma_vi += v_real * i_real #sumador del producto de voltaje*corriente


 #############################################


    # --- DETERMINAR ANGULO DE DESFASE BUSCANDO LOS POR PICOS DE CORRIENTE Y VOLTAJE---

    # Encontrar posicion del pico de VOLTAJE
    num_muestras_v = None # numero de muestras hasta el pico de voltaje
    max_v = max(volt_data) # Valor maximo de voltaje en el vector de datos
    for i in range(N): # Recorrer todo el vector de voltaje hasta encontrar el valor maximo
        if volt_data[i] == max_v: # Cuando encuentra el valor maximo guarda su posicion (i)
            num_muestras_v = i # guardar posicion del valor maximo en la nueva variable
            break

    # Encontrar posicion del pico de CORRIENTE
    num_muestras_i = None # numero de muestras hasta el pico de corriente
    max_i = max(corr_data) # Valor maximo de corriente en el vector de datos
    for i in range(N): # Recorrer todo el vector de corriente hasta encontrar el valor maximo
        if corr_data[i] == max_i: # Cuando encuentra el valor maximo guarda su posicion (i)
            num_muestras_i = i # guardar posicion del valor maximo en la nueva variable
            break

    ####### CALCULAR ANGULO #######
    modulo_v = sqrt(suma_v2) # Calcular magnitud del vector de voltaje
    modulo_i = sqrt(suma_i2) # Calcular magnitud del vector de corriente


    if modulo_v > 0 and modulo_i > 0:
        cos_angulo = suma_vi / (modulo_v * modulo_i)  # calcular coseno del angulo entre los dos vectores
        cos_angulo = max(-1.0, min(1.0, cos_angulo))  # limitar entre -1 y 1 para evitar error matematico
        angulo_radianes = acos(cos_angulo) # calcular angulo en radianes
        angulo_grados = angulo_radianes * 180 / pi  # convertir a grados
    else: 
        angulo_radianes = 0.0  # si alguno de los vectores es cero, angulo es cero
        angulo_grados = 0.0

    print("Muestra pico voltaje:", num_muestras_v) # mostrar en consola la posicion del pico de voltaje
    print("Muestra pico corriente:", num_muestras_i) # mostrar en consola la posicion del pico de corriente
    #########################################

    # --- CALCULAR POTENCIAS ---
    V_RMS = sqrt(suma_v2 / 200) #Calcular voltaje RMS usando el numero muestras N
    I_RMS = sqrt(suma_i2 / 200)/1.4 #Calcular corriente RMS usando el numero muestras N divido entre el valor de la resistencia SHUNT
                                    # que para nuestro caso tiene un valor de 1.4 ohms 

    S = V_RMS * I_RMS # Calcular potencia aparente usando valores RMS de voltaje y corriente

        # --- IDENTIFICAR VALORES PICO ---
    Vpico = max(abs(np.array(voltajes_reales))) # Encontrar valor maximo en el vector de voltaje
    Ipico = max(abs(np.array(corrientes_reales))) # Encontrar valor maximo en el vector de corriente

    P = S * cos(angulo_radianes) # Calcular potencia real usando la potencia aparente y el angulo de desfase entre voltaje y corriente 

    FP = P / S if S > 0 else 0 # Calcular factor de potencia usando la potencia real y aparente
    Q = sqrt(abs(S**2 - P**2))  # Calcular la potencia reactiva usando el triangulo de potencias

    ######### Mostrar en consola los valores obtenidos ###############
    print("\n------------- RESULTADOS -------------")
    print("V_RMS:", V_RMS) # voltaje RMS
    print("I_RMS:", I_RMS) # corriente RMS
    print("Vpico:", Vpico) # voltaje pico
    print("Ipico:", Ipico) # corriente pico
    print("FP:", FP) # factor de potencia
    print("Angulo:", angulo_grados) # angulo de desfase en grados
    print("P:", P) # potencia real
    print("Q:", Q) # potencia reactica
    print("S:", S) # potencia aparente
    ##################################################################
    # --- GRAFICAS ---
    plt.figure(figsize=(10,6)) # crear figura con tamaño 10x6 pulgadas

    # grafica superior: señal de voltaje
    plt.subplot(2,1,1) # dividir figura en 2 filas, 1 columna, grafica 1
    plt.plot(voltajes_reales) # graficar vector de voltajes reales
    plt.title("Voltaje Real") # titulo de la grafica
    plt.grid() # mostrar cuadricula

    # grafica inferior: señal de corriente
    plt.subplot(2,1,2) # dividir figura en 2 filas, 1 columna, grafica 2
    plt.plot(corrientes_reales) # graficar vector de corrientes reales
    plt.title("Corriente Real") # titulo de la grafica
    plt.grid() # mostrar cuadricula

    # construir cuadro de texto con los resultados calculados
    texto = (
        f"Vrms = {V_RMS:.2f} V\n"    # voltaje RMS
        f"Irms = {I_RMS:.2f} A\n"    # corriente RMS
        f"Vpico = {Vpico:.2f} V\n"   # voltaje pico
        f"Ipico = {Ipico:.2f} A\n"   # corriente pico
        f"P = {P:.2f} W\n"           # potencia activa
        f"Q = {Q:.2f} VAR\n"         # potencia reactiva
        f"S = {S:.2f} VA\n"          # potencia aparente
        f"FP = {FP:.3f}\n"           # factor de potencia
        f"Ang = {angulo_grados:.2f}°" # angulo de desfase
    )

    # mostrar texto con resultados en la parte derecha de la figura
    plt.gcf().text(0.75, 0.5, texto, fontsize=10, bbox=dict(facecolor='white'))

    plt.tight_layout() # ajustar espaciado entre graficas automaticamente
    plt.pause(20)   # mostrar grafica durante 20 segundos sin bloquear el codigo
    plt.close()  # cerrar figura para mostrar la siguiente actualizacion
