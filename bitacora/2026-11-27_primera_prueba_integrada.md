# Primera prueba integrada del banco: compresor, transmisor, solenoide e interfaz

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-27 · **Estado:** borrador

Continúa [la entrada de la interfaz del banco](2026-11-27_interfaz_banco.md). Primera vez que funcionan juntos el compresor, el proto-tanque, el transmisor de presión, la solenoide, el programa `banco.ino` v2 y la interfaz `banco.html`.

Todo lo de esta entrada viene del relato de Matías después de la prueba. **No hay registro de datos**: se olvidó presionar "Grabar". Existe un video de la prueba. Las cifras son las que Matías leyó en la interfaz.

## 1. Fallas encontradas antes de la prueba (dos fallas independientes, de cableado)

### 1.1 El ESP32 no encontraba el ADS1115

- **Síntoma:** al cargar `banco.ino`, el Monitor Serie repetía `ERROR: no responde el ADS1115 (SDA/SCL, VDD, 0x48)`. Un escáner I²C no encontraba nada en el bus.
- **Diagnóstico:** se revisó la cadena de alimentación y de señales con multímetro, siguiendo una tabla de 10 puntos. No había continuidad entre el **GPIO22 (SCL)** del ESP32 y el lado LV del conversor de nivel.
- **Causa:** un cable **desoldado por detrás** de la placa.
- **Solución:** se volvió a soldar. El escáner encontró el ADS en 0x48 y la interfaz empezó a leer la presión.

### 1.2 La solenoide no abría

- **Síntoma:** la interfaz y el programa `solenoide.ino` mostraban la válvula abierta, pero no sonaba el clic. La fuente pasaba de 0 a solo **0,01 A** al abrir; con la bobina energizada deberían ser ~1,7–2 A. Es decir, la orden salía del ESP32, pero la corriente no llegaba a la bobina.
- **Causa:** un **cable rojo** del cableado entre el driver y el ESP32 (la conexión de voltaje del driver) dejó de tener continuidad, **como si se hubiera cortado por dentro**, sin daño visible.
- **Solución:** Matías lo retiró y soldó un cable nuevo. La válvula volvió a abrir.

**Lección:** los dos problemas fueron de cables y soldaduras, no de código. Conviene revisar la continuidad de todo el cableado cada vez que se mueve el montaje, y reemplazar los cables de protoboard por cables soldados o con conectores firmes.

## 2. La prueba

### Montaje
- Compresor de aire, conectado al tanque por una **válvula de bola manual**.
- Proto-tanque con la cruz de 1/4", el transmisor XDB401 y la solenoide JT22-02.
- Adaptador **P2 macho–macho impreso en PETG**, reimpreso más macizo para esta prueba.
- ESP32 con `banco.ino` v2, conectado por USB a la interfaz `banco.html` en Chrome.

### Procedimiento (según Matías)
1. Con la válvula de bola se dejó entrar aire hasta la presión deseada y luego se cerró.
2. Se observó si la presión se mantenía (estanqueidad).
3. Se hicieron descargas con la solenoide desde la interfaz.
4. Se probó la función **fijar presión en 1 bar**.

### Resultados
| Aspecto | Resultado |
|---|---|
| Presión máxima | ~1,8 bar (bajo los 2 bar previstos) |
| Estanqueidad | El sistema se mantuvo **medianamente estanco**. Sobre **~1,4 bar** apareció una fuga de aire **cerca de la válvula de bola**, que Matías atribuye a un mal sellado de los o-rings. Fue la fuga principal |
| Adaptador P2 impreso | **Sin fugas** |
| Descargas con la solenoide | Funcionaron bien |
| Lectura y gráfico | Bien. Se ve más ruido que en la simulación, pero no molesta |
| Fijar presión (1 bar) | **Funcionó**, pero la válvula abría y cerraba muy seguido: el ruido de la lectura cruzaba la banda de 0,05 bar |
| Interfaz | Funcionó bien en general |
| Desconexiones del ESP32 | **~3 veces en ~15 minutos**. Matías cree, sin estar seguro, que ocurrió **cada vez que encendió el compresor** para cargar presión. Al presionar "Conectar" se recuperaba al tiro |
| Grabación de datos | **No se hizo** (olvido). Hay un video de la prueba |

## 3. Análisis de las desconexiones (hipótesis, no verificadas)

Que coincidan con el arranque del compresor apunta a una **perturbación eléctrica**, no a saturación de datos: 20 datos por segundo es muy poco para el ESP32 y para el USB. Hipótesis, de más a menos probable:

1. **Ruido o caída de voltaje al arrancar el motor del compresor.** Puede reiniciar el ESP32 o hacer que el PC pierda el dispositivo USB por un instante.
2. **Bucle de tierra** entre el PC, la fuente de 12 V y el compresor.

**Cómo distinguirlo:** si después de la desconexión el registro de eventos muestra de nuevo **"LISTO banco v2"**, el ESP32 **se reinició**. Si no lo muestra, solo se cortó el USB.

**Por confirmar:** si la válvula estaba abierta durante alguna desconexión, ¿se cerró sola? Así debería ser, por el cierre por pérdida de comunicación (2 s) o por el reinicio.

## 4. Mejoras propuestas

1. **Reconexión automática en la interfaz.** Chrome permite reabrir un puerto ya autorizado sin volver a elegirlo (`navigator.serial.getPorts()` y el evento `connect`). La interfaz reintentaría sola mientras esté abierta y lo indicaría en la barra superior.
2. **Fijar presión menos sensible al ruido:**
   - filtrar la lectura (promedio móvil de ~0,5 s) solo para decidir cuándo abrir;
   - ampliar la banda (de 0,05 a ~0,10 bar, o un porcentaje de la presión fijada);
   - pedir que la presión esté sobre la banda durante un tiempo mínimo antes de abrir.

   Hay que conservar la lectura sin filtrar para el gráfico y la grabación.
3. **Inmunidad al compresor:** enchufar el compresor en otro circuito o alargador, separar sus cables del USB y del ESP32, probar un hub USB con alimentación propia o una ferrita en el cable USB.
4. **Recordatorio de grabación:** que la interfaz avise si se abre la válvula sin estar grabando.
5. **Fuga en la válvula de bola:** revisar los o-rings y las uniones de esa zona antes de pasar de 1,4 bar.

## 5. Pendientes

- Repetir la prueba **grabando** (CSV) para tener registro cuantitativo: estanqueidad, curvas de descarga y fijar presión.
- Comparar la lectura con un manómetro de referencia (escala y linealidad).
- Corregir la fuga cerca de la válvula de bola y subir en escalones hasta 3 bar.
- Implementar las mejoras 1 y 2 y verificarlas con el compresor.
- La solenoide (latón + FKM) **no está calificada para GOX**: solo agua, aire, N₂ y queroseno.
