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

## 4. Fe de erratas (misma noche): la descarga lenta era el inyector impreso, no la solenoide

Matías aclaró la causa después de leer la sección 1:

- **La pieza negra sobre la solenoide es el inyector de prueba impreso en PLA** ([`../piezas/inyector_impreso/`](../piezas/inyector_impreso/), bitácora del 26-11), atornillado a la salida de la válvula.
- **Salió mal impreso.** El orificio quedó mucho más chico que el diseñado (Ø2), sin medir todavía, y el cono de aire salía **hacia un solo lado** (la izquierda), no simétrico.
- **Lo dejó a propósito**, para ver cómo se comporta el sistema con una obstrucción, como pasaría en un caso real.

Por lo tanto:

- La **hipótesis 3** de la sección 1 (restricción en la salida) era la correcta. Las hipótesis 1 (válvula de piloto que no abre del todo) y 2 (válvula al revés) **se descartan como causa** de esta descarga lenta.
- **Paso efectivo del inyector mal impreso:** el ~1,2–1,3 mm estimado en la sección 1 sería el del inyector, no el de la válvula. Sigue siendo una estimación gruesa, porque el volumen del tanque no está medido. Es menor que el Ø2 del diseño, lo que calza con un orificio parcialmente tapado por la impresión.
- **Prueba de descarga libre:** con ~1,6 bar, Matías desconectó el acople rápido del compresor y abrió la llave de entrada. El aire salió de golpe, muy rápido, e incluso **hizo temblar el tanque** por el empuje. Esa descarga sale por la llave y el acople, no por la solenoide.
- **Estado de la solenoide:** según Matías, con la válvula abierta se comporta bien. **No hay todavía una descarga medida por la solenoide sin el inyector**; conviene hacerla para tener la curva de referencia.

**Para la próxima prueba**, el pendiente 4 de la sección 3 queda así:
- grabar una descarga por la solenoide **sin** el inyector y otra **con** el inyector;
- medir el orificio del inyector mal impreso (con una broca o aguja calibrada como galga);
- reimprimir el inyector revisando la configuración: la orientación, los soportes internos y la calibración de flujo de la impresora.

Con eso, la diferencia entre las dos curvas da el paso efectivo del inyector.

## 5. Otras observaciones del video (segunda revisión)

Las observaciones salen de cuadros del video cada 2,5 s. Son lo que se ve, no mediciones.

- **Consumo real de la solenoide abierta:** la fuente marca **0,78–0,80 A a 11,6 V** con la válvula abierta en mantención al 70 % (0:37 y 1:27–1:45). Eso son ~9 W sostenidos. **Corrige** el "~0,2 A" anotado de memoria en la [entrada del 26-11](2026-11-26_transmisor_presion_prueba.md) (sección 6). Con la válvula cerrada marca 0,00 A.
- **No se ve un regulador ni una válvula de alivio** entre el compresor y el tanque. La entrada se dosifica con la llave manual. Un compresor de taller puede llegar a ~8 bar. La única protección contra sobrepresión es la purga del ESP32, que depende del transmisor y de que la salida esté libre (y en esta prueba la salida tenía el inyector parcialmente tapado).
- **El operador carga a mano, junto al tanque presurizado**, con la mano en la llave y cerca del niple P2 impreso.
- **Fijación del tanque:** el extintor está de pie en el suelo, sujeto con cinta de papel a una caja de cartón. En la descarga libre el tanque **tembló por el empuje**.
- **La solenoide queda en voladizo** sobre el niple P2 impreso, con el peso de la bobina, el conector y el cable. Si el tanque vibra, eso carga a flexión una pieza de plástico.
- **Electrónica:** la caja de cartón con el ESP32, el ADS y el driver va amarrada al tanque. El cable rojo de +12 V cuelga suelto desde la fuente. El compresor está en el suelo a ~1 m de la electrónica.
- **Gráfico:** con la purga en 4 bar, las presiones de la prueba (0,3–1,6 bar) ocupan solo el tercio inferior del gráfico.

### Recomendaciones antes de subir de presión
1. **Válvula de alivio mecánica** en el tanque o en la cruz, tarada bajo el límite de las piezas impresas (por ejemplo 4–5 bar), y **regulador** a la salida del compresor, ajustado a la presión del ensayo (≤ 3 bar por ahora). Son la protección real; la purga del ESP32 es una segunda capa.
2. **Operar a distancia**, desde el notebook. Si se carga a mano, que sea a baja presión y sin la cara sobre el niple impreso. Para presiones mayores, una pantalla de policarbonato o el container que menciona el documento de la Fase 1.
3. **Fijar el tanque** a una base o a la mesa con una correa o abrazadera, sobre todo para las descargas libres.
4. **Sostener la solenoide** con un soporte propio, para que el niple P2 no cargue su peso.
5. **Ordenar el cableado:** una caja firme, cables soldados o con conectores, alivio de tensión en el cable de la fuente y el USB lejos de los cables del compresor.
6. **Ensayo de calentamiento de la bobina:** a ~9 W, conviene medir su temperatura tras 60 s abierta antes de usar aperturas largas. Hoy el máximo es 60 s.
7. **Hipótesis para las desconexiones:** si ocurren ~15 s después de encender el compresor, puede coincidir con el corte de su presostato o la descarga de su válvula de alivio interna (motor que se detiene y pico eléctrico). Vale la pena anotar si coincide con ese "pssst" del compresor.

## 6. Corrección del simulador

El simulador del modo demo se había ajustado a la descarga lenta del video, que se debía al inyector tapado. Pedido por Matías, vuelve a los valores anteriores (carga 0,12 bar/s, descarga rápida). Son provisorios: se ajustarán cuando haya datos crudos grabados. Se mantienen la lógica v3 y el ruido de ±0,03 bar.

## 7. Temperatura de la bobina y escala del gráfico

- **Bobina (observación de Matías):** en los ~15 min de prueba abrió y cerró muchas veces. Las aperturas más largas fueron de ~30–40 s, nunca de 60 s. Al guardar el sistema, la bobina estaba **tibia, no caliente**. Es cualitativo, sin medición. Queda como pendiente medir su temperatura después de una apertura de 60 s.
- **Gráfico con escala comprimida** (pedido por Matías): el eje vertical usa la raíz cuadrada de la presión, así que el tramo de 0–1 bar ocupa más espacio que el de 1–2, y así sucesivamente. Las marcas quedan en 0; 0,25; 0,5; 1; 1,5; 2; 3; 4… El botón "Escala: comprimida / lineal", junto al título del gráfico, cambia entre las dos y se recuerda. Ojo: en la escala comprimida, una subida lineal se ve como una curva; para leer pendientes conviene la lineal.

**Corrección de la escala (misma noche):** la raíz cuadrada agrandaba mucho el ruido cerca de 0. Su pendiente es infinita en 0, así que una oscilación de milésimas se veía enorme. Se cambió por una escala logarítmica suave, ln(1 + p/0,5): de 0 a 1 bar sigue ocupando ~la mitad del alto hasta 4 bar, pero cerca de 0 solo amplía unas 2 veces respecto de la escala lineal. Las marcas quedan en 0; 0,5; 1; 1,5; 2; 3; 4. El ruido del simulador se mantiene en ±0,03 bar. Matías aclaró que en el banco real la lectura en reposo oscila del orden de 0,00 a 0,03 bar, y probablemente algo más (al describirlo primero había agregado un cero de más).
