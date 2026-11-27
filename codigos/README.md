# Códigos — IGNIS

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5)
> **Fecha:** 2026-11-21 · **Estado:** borrador
> **Editado por:** Claude (Opus 5.5), 2026-11-26 — agrega `presion/`
> **Editado por:** Claude (Sonnet 5.5), 2026-11-26 — `presion/` v2 (canal A1) tras probarlo
> **Editado por:** Claude (Opus 5.5), 2026-11-27 — agrega `banco/` e `interfaz/`

Aquí vive todo el código del proyecto (control, adquisición de datos, pruebas). Cada componente tiene su propia carpeta, y dentro de ella el programa lleva el mismo nombre que la carpeta. Esa regla es la que exige Arduino IDE para abrir un sketch.

```
codigos/
  solenoide/solenoide.ino
  presion/presion.ino
  banco/banco.ino          (presión + válvula + seguridad, para usar con la interfaz)
  interfaz/banco.html      (página para Chrome; no es un sketch)
```

## Contenido

| Carpeta | Qué hace | Hardware | Estado |
|---|---|---|---|
| [`solenoide/`](solenoide/solenoide.ino) | Abre y cierra la solenoide JT22-02 por el Monitor Serie (`open`, `close`, `status`, `hold NN`) | ESP32 DevKit + driver DRV8871 | probado sin presión |
| [`banco/`](banco/banco.ino) | Programa único del banco: lee la presión a 20 Hz y maneja la válvula (abrir, cerrar, pulso de N s). Seguridad local: cierra al perder la comunicación, purga automática sobre un límite (máx. 8 bar), tiempo máximo abierta. Cero y límites guardados en la memoria del ESP32 | ESP32 + ADS1115 (A1) + XDB401 + DRV8871 + JT22-02 | revisado en sintaxis, **sin probar en el hardware** |
| [`interfaz/banco.html`](interfaz/banco.html) | Interfaz de operación por USB (Web Serial, Chrome/Edge): presión grande con zonas de color, gráfico de 30 s, botón abrir/cerrar, pulso, límites, cero y grabación a CSV. `?demo` la muestra con un simulador | PC con Chrome | probada en modo demo |
| [`presion/`](presion/presion.ino) | Lee el transmisor XDB401 (0–40 bar, 0,5–4,5 V) con ADS1115 y entrega CSV `t_ms,volts,bar`; comandos `zero` / `reset` | ESP32 + ADS1115 + XDB401 | probado a presión atmosférica (ver bitácora del 2026-11-26) |

## Cómo usarlos

- Abrir el `.ino` con Arduino IDE (placa **ESP32 Dev Module**, core Arduino-ESP32 3.x).
- El cableado y las pruebas de cada programa están en las entradas de [`../bitacora/`](../bitacora/README.md).
- Cada programa debe llevar en su cabecera las conexiones y los comandos, y un comentario si cambia el comportamiento respecto a la versión anterior.

## Interfaz del banco (`banco/` + `interfaz/`)

1. Cargar `banco/banco.ino` en el ESP32. **Cerrar el Monitor Serie de Arduino IDE** (el puerto solo lo puede usar un programa a la vez).
2. Abrir `interfaz/banco.html` con doble clic en **Chrome o Edge** y presionar **Conectar**; elegir el puerto del CP2102.
3. Con el tanque abierto, presionar **Cero**. Revisar **Alarma**, **Purga** y **Máx. abierta**, y **Aplicar** (quedan guardados en el ESP32).
4. **Grabar** antes de cada ensayo; al detener se descarga un CSV (`t_s, volts, bar, valvula, flags, evento`).
5. **Esc** o la **barra espaciadora** cierran la válvula. Si se cierra la página, se desconecta el cable o se cuelga el PC, el ESP32 cierra la válvula a los 2 s.

La purga automática abre la válvula de descarga al superar la presión fijada y la cierra 0,3 bar más abajo. **No reemplaza** al regulador ni a la válvula de alivio: depende de que el transmisor funcione y de que la descarga esté libre.
