from machine import Pin, ADC  # importar clases para manejar pines y ADC
import utime                   # importar libreria de tiempo de micropython
import array                   # importar libreria para vectores de datos

# configurar ADC de voltaje en pin 32
adc_v = ADC(Pin(32))
adc_v.atten(ADC.ATTN_11DB)    # rango de entrada 0 a 3.3V
adc_v.width(ADC.WIDTH_9BIT)   # resolucion de 9 bits (0 a 511)

# configurar ADC de corriente en pin 33
adc_i = ADC(Pin(33))
adc_i.atten(ADC.ATTN_11DB)    # rango de entrada 0 a 3.3V
adc_i.width(ADC.WIDTH_9BIT)   # resolucion de 9 bits (0 a 511)

N = 200  # numero de muestras por periodo de la señal 
ADC_MEDIO = 228  # valor del ADC cuando la señal esta en cero (offset)


# vectores para almacenar las muestras crudas del ADC
volt_muestras = array.array('H', [0]*N)       # vector de voltaje
corriente_muestras = array.array('H', [0]*N)  # vector de corriente

while True:
    #DETECAR CRUCE POR CERO DE VOLTAJE
    # esperar hasta que el voltaje pase de negativo a positivo
    while True:
        v_anterior = adc_v.read() # leer muestra actual
        v_actual = adc_v.read() #leer muestra siguiente
        #DETECTAR CRUCE POR CERO
        # Validar que la muestra anterior este bajo el centro y la actual sobre el centro
        if v_anterior < ADC_MEDIO and v_actual >= ADC_MEDIO:
            break # cruce detectado, empeza a capturar
    
    #MUESTRAR SEÑAL DE CORRIENTE Y VOLTAJE (tomar 200 muestras por periodo de la señal)
    for i in range(N):
        volt_muestras[i] = adc_v.read()  # leer y guardar muestra de voltaje
        utime.sleep_us(1) #esperar 1 microseg para tomar otra muestra 
    for i in range(N):
        corriente_muestras[i] = adc_i.read() # leer y guardar muestra de corriente
        utime.sleep_us(1) #esperar 1 microseg para tomar otra muestra
    
    # TRANSMITIR DATOS POR SERIAL
    print("START")  # inicio de transmision
    for i in range(N):
        print("{},{}".format(volt_muestras[i], corriente_muestras[i]))  # enviar datos de voltaje y corriente separados por una coma (voltaje,corriente)
    print("END") # fin de transmision

    utime.sleep(2) # esperar 2 segundos para que se repita el ciclo