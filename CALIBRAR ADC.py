### CALIBRAR ADC_MEDIO
from machine import Pin, ADC # importar clases para manejar pines y ADC
import time   # importar libreria de tiempo

# configurar ADC de voltaje en pin 32
adc_v = ADC(Pin(32))
adc_v.atten(ADC.ATTN_11DB)    # rango de entrada 0 a 3.3V
adc_v.width(ADC.WIDTH_9BIT)   # resolucion de 9 bits (0 a 511)

# configurar ADC de corriente en pin 33
adc_i = ADC(Pin(33))
adc_i.atten(ADC.ATTN_11DB)    # rango de entrada 0 a 3.3V
adc_i.width(ADC.WIDTH_9BIT)   # resolucion de 9 bits (0 a 511)
 
minv = 511 # incializar valor minimo posible de ADC pin de voltaje
maxv = 0 # inicializar valor maximo posible de ADC pin de corriente
mini = 511  # inicializar valor minimo posible de ADC pin de voltaje
maxi = 0 # inicializar valor maximo posible de ADC pin de corriente

# tomar 2000 muestras para encontrar los valores minimos y maximos reales
for _ in range(2000):
    v = adc_v.read()  # leer muestra de voltaje
    i = adc_i.read()  # leer muestra de corriente
    if v < minv: minv = v  # actualizar minimo de voltaje
    if v > maxv: maxv = v  # actualizar maximo de voltaje
    if i < mini: mini = i  # actualizar minimo de corriente
    if i > maxi: maxi = i  # actualizar maximo de corriente
    time.sleep_ms(1)       # esperar 1ms entre muestras
    
# imprimir resultados: el centro es el offset DC de cada señal (ADC_MEDIO)
print("Voltaje - min:", minv, "max:", maxv, "centro:", (minv+maxv)//2)
print("Corriente - min:", mini, "max:", maxi, "centro:", (mini+maxi)//2)