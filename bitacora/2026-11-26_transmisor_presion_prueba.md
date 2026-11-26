# Primera prueba del transmisor de presión: el cable estaba soldado en A1

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5)
> **Fecha:** 2026-11-26 · **Estado:** borrador

Continúa la sección 2 de [la entrada inicial del 26-11](2026-11-26_inyector_elemento_y_mini_motor.md), donde se dejó el plan de prueba del transmisor sin ejecutar, y la entrada del [21-11](2026-11-21_solenoide_driver_esp32.md), donde se cableó la solenoide.

## 1. Objetivo

Verificar que el transmisor XDB401 (0–40 bar, salida 0,5–4,5 V, alimentado a 12 V) se lee bien con el ADS1115 y el ESP32, a presión atmosférica, antes de subir presión con aire. Todo se hizo **sin presión** (tanque abierto).

## 2. Montaje (todo soldado y conectado ese día)

| Conexión | Detalle |
|---|---|
| Fuente +12 V | VM del driver DRV8871 y cable rojo del transmisor |
| Fuente − | GND del driver; es la tierra común |
| Tierras | GND del ESP32, del ADS, del conversor de nivel y cable negro del transmisor, todos unidos |
| Cable amarillo del transmisor | **ADS1115 A1** (soldado ahí; el código v1 leía A0) |
| ADS1115 VDD | 5 V (VIN del ESP32, por USB); ADDR a GND (0x48) |
| SDA / SCL | Conversor de nivel → GPIO21 / GPIO22 |
| Solenoide | OUT1/OUT2 del driver; IN1/IN2 a GPIO26/GPIO27 |

La fuente es única, con una sola salida (todavía no hay una dedicada por componente).

## 3. Cronología de la prueba

1. **Continuidad de GND y de 12 V:** sin cortos, tierras unidas. Verificado con multímetro por Matías.
2. **Alimentación energizada:** 5 V en el VDD del ADS y 0,502 V en el cable amarillo con el tanque abierto. Medido con multímetro contra el GND de la fuente.
3. **Primera lectura con `presion.ino` v1:** el Monitor Serie mostraba `volts ≈ 0,65` y `bar ≈ +1,5`, estable (±0,002 V). Esa lectura **no coincidía** con el multímetro: A0 contra GND del ADS daba 0,501 V y el amarillo contra el negro del transmisor daba lo mismo.
4. **`zero` a presión atmosférica:** el programa respondió un offset de unos 1,47 bar (cifra recordada por Matías, no registrada) y las lecturas bajaron a 0,01–0,06 bar. El cero ocultó el problema: los volts seguían en ~0,65.
5. **Soplido en el sensor:** Matías lo desmontó, sopló y no vio variación en la lectura. Después **apagó la fuente de 12 V** (solo el ESP32 quedó encendido) y la lectura se mantuvo en ~0,65 V. Sin energía en el transmisor, el ADS seguía mostrando lo mismo: no estaba midiendo al sensor.
6. **Unir A0 a GND** no la bajó a 0 V.
7. Matías revisó la soldadura y vio que el amarillo estaba en **A1**, no en A0. El pin A0 quedaba flotando y mantenía un valor cualquiera.
8. **Código `presion.ino` v2:** canal configurable (`CANAL = 1`). Con eso, lectura correcta.

## 4. Resultado (reportado por Matías, de memoria)

- Con el tanque abierto y el cable amarillo en A1, los volts coinciden con el multímetro (~0,50 V).
- **Cifras de memoria, no registradas y sin confirmar.** Matías recuerda que la lectura en reposo era un pequeño valor **negativo** y que al soplar subió a un valor **positivo** de la misma magnitud (mismo número de decimales). Lo más probable es **−0,05 bar en reposo y +0,040 bar al soplar**, es decir, un salto de unos 0,09 bar. Una primera versión de esta entrada decía −0,005 y 0,004; era un cero de más, y queda corregida aquí. Es un salto razonable para un soplido fuerte de boca (del orden de 0,05–0,15 bar) y confirma que el sensor responde.
- **Por repetir con registro:** anotar la lectura en reposo y el máximo al soplar, o mejor, probar con una referencia (jeringa o manómetro).
- El cero se ajustará más adelante.

**Estado:** el transmisor y la cadena de lectura **funcionan a presión atmosférica**. No se ha comprobado a presión real: ni la escala, ni la linealidad, ni la estabilidad al conmutar la solenoide.

## 5. Problemas y correcciones

- **Causa raíz del desfase de 0,15 V:** el cable amarillo estaba soldado en A1 y el código v1 leía A0. A0 flotaba, y un pin sin conexión conserva un valor que no depende de nada. Mi diagnóstico inicial apuntó a una tierra mal unida o a presión atrapada. Ninguna de las dos hipótesis era la causa, aunque se descartaron con mediciones.
- **Mejor prueba para el futuro:** apagar la fuente y ver si la lectura cae a ~0. Esa sola prueba bastó para ver que el ADS no leía al sensor.
- **`zero` demasiado pronto:** hacer `zero` antes de entender un desfase ocultó el problema por un rato. Conviene hacer primero la comparación contra el multímetro.
- **Interpretación errónea del 0,502 V:** el valor que dio Matías al principio era del multímetro, no del serial, y esa ambigüedad costó unos minutos.

## 6. Consumo en los 12 V (estimación, no medida)

- **Solenoide abierta, en mantención:** la fuente mostraba unos 0,2 A (lectura de Matías). Tomando 0,5 A como peor caso por el error del instrumento, queda holgura frente al límite de 2,5 A.
- **Pico de apertura:** ~1,7–2 A durante 300 ms, justo bajo el límite interno de ~2,1 A del DRV8871 (ILIM = 30 kΩ).
- **ADS1115, conversor de nivel y ESP32:** no están en los 12 V; se alimentan del 5 V / 3,3 V del USB del PC. Los consumos son del orden de 0,15 mA (ADS) y ~1 mA (conversor), **valores típicos de hoja de datos, de memoria**.
- **Transmisor:** unos pocos mA a 12 V. No se midió.
- **Lo que sí los puede dañar es el voltaje**: si los 12 V tocan un pin del ADS (máximo absoluto ~7 V). Se recomendó una resistencia de **1 kΩ en serie en la señal amarilla** como protección ante un corto accidental; **no se ha instalado**.

## 7. Pendientes

1. **Prueba con presión real:** aire en escalones de 0,5 / 1 / 2 / 3 bar, comparando con un manómetro de referencia. Después, agua hasta 8 bar máximo con válvula de alivio.
2. **Verificar la escala** (span) y la linealidad frente al manómetro.
3. **Ruido al conmutar la solenoide:** comprobar si la lectura salta con el clic. Si salta, agregar un condensador de ~100 µF cerca del transmisor.
4. Instalar la resistencia de 1 kΩ en serie en el cable amarillo.
5. Probar la solenoide con aire (presión mínima de apertura a 0,5 / 1 / 2 bar) y medir su corriente real.
6. Armar un solo programa que lea el transmisor y maneje la solenoide (hoy se cargan por separado).
7. Actualizar `Fase1_seleccion_electronica.md`: el transductor real es el XDB401 de 0,5–4,5 V con ADS1115, no el Veto 4–20 mA con SEN0262.
8. Fuente dedicada por componente y sujeción mecánica de la solenoide.
9. La solenoide (latón + FKM) **no está calificada para GOX**: solo agua, aire, N₂ y queroseno.

## 8. Archivos

- Código: [`../codigos/presion/presion.ino`](../codigos/presion/presion.ino) (v2, canal configurable) y [`../codigos/solenoide/solenoide.ino`](../codigos/solenoide/solenoide.ino) (v2, sin cambios).
