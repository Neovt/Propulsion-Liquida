# Códigos — IGNIS

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5)
> **Fecha:** 2026-11-21 · **Estado:** borrador
> **Editado por:** Claude (Opus 5.5), 2026-11-26 — agrega `presion/`
> **Editado por:** Claude (Sonnet 5.5), 2026-11-26 — `presion/` v2 (canal A1) tras probarlo
> **Editado por:** Claude (Opus 5.5), 2026-11-27 — agrega `banco/` e `interfaz/`; actualiza a banco v3

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
| [`solenoide/`](solenoide/solenoide.ino) | Prueba suelta de la válvula. Abre y cierra la solenoide JT22-02 por el Monitor Serie (`open`, `close`, `status`, `hold NN`) | ESP32 DevKit + driver DRV8871 | probado sin presión |
| [`banco/`](banco/banco.ino) | **Programa vigente del banco.** Lee la presión a 20 Hz y maneja la válvula (abrir, cerrar, pulso de N s, fijar presión por descarga). Seguridad local: cierra al perder la comunicación, purga sobre un límite (máx. 8 bar), tiempo máximo abierta. v3: decisiones con presión filtrada y fijar presión menos sensible al ruido. Cero y límites guardados en el ESP32 | ESP32 + ADS1115 (A1) + XDB401 + DRV8871 + JT22-02 | v2 probada con aire hasta ~1,8 bar; **v3 sin probar en el hardware** |
| [`interfaz/banco.html`](interfaz/banco.html) | Interfaz de operación por USB (Web Serial, Chrome/Edge): presión filtrada en grande con zonas de color, gráfico de 60 s, abrir/cerrar, pulso, fijar presión, límites y cero. **Reconexión automática** y **registro de sesión siempre activo** ("Descargar sesión"), además de Grabar por tramos. `?demo` abre un simulador con la misma lógica | PC con Chrome | probada con el banco real (v2); reconexión sin probar con USB real |
| [`presion/`](presion/presion.ino) | Prueba suelta del transmisor. Lee el transmisor XDB401 (0–40 bar, 0,5–4,5 V) con ADS1115 y entrega CSV `t_ms,volts,bar`; comandos `zero` / `reset` | ESP32 + ADS1115 + XDB401 | probado a presión atmosférica (ver bitácora del 2026-11-26) |

## Cómo usarlos

- Abrir el `.ino` con Arduino IDE (placa **ESP32 Dev Module**, core Arduino-ESP32 3.x).
- El cableado y las pruebas de cada programa están en las entradas de [`../bitacora/`](../bitacora/README.md).
- Cada programa debe llevar en su cabecera las conexiones y los comandos, y un comentario si cambia el comportamiento respecto a la versión anterior.

## Interfaz del banco (`banco/` + `interfaz/`)

1. Cargar `banco/banco.ino` en el ESP32. **Cerrar el Monitor Serie de Arduino IDE**, porque el puerto solo lo puede usar un programa a la vez.
2. Abrir `interfaz/banco.html` con doble clic en **Chrome o Edge**.
   - La primera vez, presionar **Conectar** y elegir el puerto del CP2102.
   - Desde entonces la página se conecta sola al abrirla, y **se reconecta sola** si se corta el USB.
3. Con el tanque abierto, presionar **Cero**. Revisar **Alarma**, **Purga** y **Máx. abierta**, y presionar **Aplicar**: quedan guardados en el ESP32.
4. **Todo queda registrado desde que se conecta.** Al terminar, **Descargar sesión** baja el CSV completo. **Grabar** sirve para guardar un ensayo en particular. Columnas: `t_s, hora, t_esp_ms, volts, bar, bar_filtrada, valvula, flags, evento`.
5. **Esc** o la **barra espaciadora** cierran la válvula. Si se cierra la página, se desconecta el cable o se cuelga el PC, el ESP32 cierra la válvula a los 2 s.

La purga automática abre la válvula de descarga al superar la presión fijada y la cierra 0,3 bar más abajo. **No reemplaza** al regulador ni a la válvula de alivio: depende de que el transmisor funcione y de que la descarga esté libre.
