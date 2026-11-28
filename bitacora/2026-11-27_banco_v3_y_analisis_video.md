# Banco v3 (reconexión, registro de sesión, fijar presión robusto) y análisis del video de la prueba

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-27 · **Estado:** borrador

Continúa [la primera prueba integrada](2026-11-27_primera_prueba_integrada.md). Tiene dos partes:

1. Lo que se ve en el video de una prueba intermedia (~1 min 51 s). No hay datos grabados, así que las cifras se leyeron en la pantalla del notebook dentro del video. Son aproximadas.
2. Las mejoras implementadas a partir de esa prueba: firmware `banco.ino` v3 e interfaz `banco.html`.

## 1. Lo que muestra el video

### Montaje visible
- Proto-tanque: extintor rojo con la cruz de acero inoxidable sobre el cuello.
  - **Arriba**, la solenoide JT22-02 de latón, con la bobina y el conector DIN de LED.
  - **Al costado**, la llave manual de entrada, conectada al compresor por una manguera en espiral.
- El compresor (verde) está **en el suelo, junto al mueble** de la electrónica.
- La fuente de laboratorio marca ~11,6–11,7 V. Con la válvula cerrada no hay consumo.

### Lecturas aproximadas en la pantalla

| Tiempo en el video | Lectura | Qué pasa |
|---|---|---|
| 0:15 → 0:25 | 1,07 → 1,57 bar | Carga con el compresor (~0,05 bar/s) |
| 0:30 | 1,58 bar | Llave de entrada cerrada |
| 0:45 → 1:10 | 1,03 → ~0,5 bar | Descarga con la solenoide abierta. A los 0:52 la interfaz marca "ABIERTA 16,2 s" |
| 1:15 → 1:20 | — | Recarga con la llave |
| 1:25 → 1:45 | 0,94 → 0,59 → 0,36 bar | Segunda descarga, válvula abierta |

### Observación principal: la descarga es mucho más lenta de lo esperado

Con la válvula abierta, la presión baja ~0,5 bar en ~15–20 s.

Una estimación gruesa indica que el **orificio de 5 mm** del anuncio debería hacerlo en el orden de **1 s**. La estimación supone:
- un tanque de unos 14 L, volumen no medido;
- flujo crítico de aire;
- un coeficiente de descarga de 0,8.

La descarga observada equivale, en cambio, a un paso efectivo de **~1,2–1,3 mm**.

**Hipótesis** (sin verificar, por orden de probabilidad):
1. **La válvula no abre por completo.** La JT22-02 parece ser de tipo **servoasistida (piloto + diafragma)**. Esas válvulas necesitan una **diferencia de presión mínima** para que el diafragma levante. Con ~1 bar o menos, solo pasaría aire por el orificio piloto, de ~1 mm, lo que **coincide con el paso efectivo estimado**. Era el pendiente "presión mínima de apertura" de la Fase 1.
2. **La válvula está instalada al revés.** Tiene una flecha de flujo. Si el flujo entra por la salida, una válvula de piloto puede no abrir bien o dejar pasar poco.
3. **Restricción en la salida.** Sobre la válvula se ve una pieza negra. Si es un silenciador o un tapón perforado, limita el caudal.

**Cómo comprobarlo:**
- Revisar el sentido de la flecha y qué hay en la salida.
- Comparar el tiempo de descarga desde 0,5, 1, 2 y 3 bar. Con una válvula de piloto, la descarga debería volverse mucho más rápida sobre cierta presión.
- Grabar la sesión para tener la curva.

**Por qué importa:**
- Explica por qué **fijar presión** abría y cerraba tan seguido: cada apertura baja muy poco la presión, y el ruido la hacía cruzar el umbral.
- Para el futuro sistema de alimentación con queroseno, una válvula que no abre del todo a baja diferencia de presión **limitaría el caudal**.

## 2. Mejoras implementadas

### Firmware `banco.ino` v3 ([código](../codigos/banco/banco.ino))
- **Presión filtrada** con un filtro de primer orden (constante de tiempo 0,5 s). Todas las decisiones la usan: fijar presión, alarma y purga. El dato crudo se sigue enviando y grabando.
- **Fijar presión menos sensible al ruido:**
  - La banda es el **mayor entre 0,10 bar y el 5 % de la presión fijada** (antes, 0,05 bar).
  - La presión filtrada tiene que estar **0,5 s seguidos** sobre la banda antes de abrir.
  - El resto no cambia: cierra al llegar a la fijada + 0,02 y espera 1 s entre aperturas.
- Cada dato trae la **presión filtrada** como 7.ª columna: `D,t_ms,volts,bar,valvula,flags,bar_filtrada`.
- Al arrancar envía "LISTO banco v3".

### Interfaz `banco.html` ([página](../codigos/interfaz/banco.html))
- **Reconexión automática:**
  - Si se corta la conexión sin haber presionado Desconectar, la interfaz pasa a **"Reconectando…"** (punto ámbar) y reintenta cada 1,5 s con el mismo puerto, sin pedir que se elija otra vez.
  - También reconecta en cuanto Windows vuelve a ver el ESP32.
  - Al abrir la página, si ya hay un puerto autorizado, **se conecta sola**.
  - "Cancelar" detiene los reintentos.
- **Registro de sesión siempre activo:**
  - Todo lo que llega desde la primera conexión (datos y eventos) queda guardado, aunque no se presione Grabar. Incluye las desconexiones y reconexiones.
  - El botón **"Descargar sesión"** lo baja como CSV. Caben unas 6 h.
  - Al cerrar la página con datos sin descargar, el navegador pregunta antes.
  - **Grabar** sigue sirviendo para guardar tramos (un ensayo en particular), y ya no se corta si la conexión se cae.
- **CSV nuevo:** `t_s, hora, t_esp_ms, volts, bar, bar_filtrada, valvula, flags, evento`. Se agregó la hora del PC porque el reloj del ESP32 se reinicia si el ESP32 se reinicia.
- **El número grande muestra la presión filtrada:** se lee más estable. El gráfico sigue mostrando la lectura cruda.
- **Simulador (`?demo`):** usa la misma lógica v3 que el ESP32, con ruido de ±0,03 bar y las tasas del video (carga ~0,05 bar/s, descarga de 1,0 a 0,5 bar en ~20 s).

### Verificación
- **Firmware:** pasó la revisión de sintaxis con sustitutos de las bibliotecas. **No está compilado para el ESP32 ni probado en el hardware.**
- **Interfaz en modo demo** (Chrome sin interfaz gráfica, sin errores de JavaScript):
  - Sin carga y con ruido de ±0,03 bar, fijar presión en 0,6 bar no abrió **ninguna vez en 20 s** y quedó en 0,61 bar.
  - El CSV de sesión se descargó con datos y eventos.
- **No verificado:** la reconexión automática necesita el puerto USB real, porque el modo demo no usa Web Serial.

## 3. Pendientes para la próxima prueba

1. Cargar `banco.ino` v3. Debe decir "LISTO banco v3".
2. **Prueba de seguridad:** con la válvula abierta, desconectar el USB a propósito. Debe cerrarse en ~2 s y la interfaz debe reconectarse sola.
3. **Descargar la sesión** al final, siempre.
4. Medir el **tiempo de descarga** desde 0,5, 1, 2 y 3 bar, y revisar la flecha de la válvula y la pieza de la salida (sección 1).
5. Alejar el compresor de la electrónica y ver si siguen las desconexiones.
