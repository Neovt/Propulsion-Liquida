# Interfaz y programa único del banco de ensayo (presión + solenoide)

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-27 · **Estado:** borrador

## 1. Objetivo

Con el transmisor y la solenoide funcionando por separado ([prueba del 26-11](2026-11-26_transmisor_presion_prueba.md)), preparar la primera prueba con el compresor: un solo programa en el ESP32 y una interfaz sencilla tipo HMI para abrir y cerrar la válvula, ver la presión y registrar los datos.

## 2. Decisiones (acordadas con Matías)

| Tema | Decisión |
|---|---|
| Enlace | USB con cable largo. WiFi/Bluetooth queda para después |
| Interfaz | Página HTML local en Chrome (Web Serial); no requiere instalar nada |
| Muestreo | 20 datos por segundo (cada uno promedia 4 lecturas del ADS a 250 SPS). Suficiente para estas presiones y no satura el ESP32 |
| Válvula | Abrir/cerrar como función principal; pulso de N segundos configurable como función secundaria |
| Pérdida de comunicación | La válvula se cierra a los 2 s (estado seguro; la solenoide es NC) |
| Sobrepresión | Alarma (aviso) y **purga automática**: sobre la presión de purga la válvula se abre para descargar y se cierra 0,3 bar más abajo |
| Límites iniciales | Alarma 3 bar, purga 4 bar. La purga no se puede fijar sobre 8 bar (piezas impresas) |
| Gráfico | Últimos 60 s |

## 3. Lo hecho

- [`../codigos/banco/banco.ino`](../codigos/banco/banco.ino): lectura (A1), control de la válvula (misma lógica v2 de mantención al 70 %), comandos `OPEN`, `CLOSE`, `PULSE s`, `ZERO`, `ALARM`, `PURGE`, `MAXOPEN`, latido `HB`, y tiempo máximo abierta (60 s por defecto). Cero y límites se guardan en la memoria del ESP32.
- [`../codigos/interfaz/banco.html`](../codigos/interfaz/banco.html): presión grande con colores por zona, barra con las marcas de alarma y purga, máximo de la sesión, estado de la válvula con tiempo abierta, botón grande abrir/cerrar, pulso, gráfico de 60 s con las aperturas marcadas, ajustes, cero, registro de eventos y grabación a CSV.
- Modo demostración (`banco.html?demo`) con un simulador del tanque.

## 4. Verificado y no verificado

- **Verificado:** el programa del ESP32 pasa una revisión de sintaxis en un compilador de PC con sustitutos de las bibliotecas (no es una compilación para ESP32). La interfaz se probó en modo demo con Chrome sin interfaz gráfica: conexión, abrir/cerrar, pulso de 3 s (cerró a los 3,04 s), purga automática, cambio de límites y descarga del CSV, sin errores de JavaScript.
- **No verificado:** compilación real en Arduino IDE, comunicación con el ESP32 real, latido y cierre por pérdida de comunicación en el hardware, y comportamiento a presión.

## 5. Antes de la prueba con compresor

1. Compilar y cargar `banco.ino`; cerrar el Monitor Serie antes de conectar la interfaz.
2. Probar sin presión: abrir, cerrar, pulso y **desconectar el cable USB con la válvula abierta** (debe cerrarse sola).
3. Cero con el tanque abierto.
4. El adaptador intermedio se reimprimirá en PETG, más macizo. Subir de a poco (0,5 / 1 / 2 / 3 bar), con regulador y válvula de alivio, y comparar con un manómetro.
5. Probar la purga con un límite bajo (por ejemplo 1 bar) antes de confiar en ella.

## 6. Actualización (misma noche): gráfico de 60 s, carga de la demo y "fijar presión"

- **Gráfico:** pasa de 30 a 60 s, con marcas cada 10 s.
- **Botón "Detener carga":** pequeño, en la barra superior. **Solo funciona en el modo demo** (detiene el compresor simulado); con el ESP32 real aparece deshabilitado, porque el banco aún no tiene válvula de carga. La carga real se corta a mano en el compresor o el regulador.
- **Fijar presión** (`banco.ino` v2, comando `SET b`): se ingresa una presión y el sistema **descarga** con la solenoide hasta llegar a ella, y la mantiene si sube. Solo puede **bajar** la presión.
  - Abre si la presión está más de 0,05 bar sobre la fijada; cierra al llegar a fijada + 0,02 (anticipo por el retardo de la válvula); espera 1 s a que se asiente antes de volver a abrir.
  - Se cancela con "Cancelar", con abrir, cerrar o pulso manual, al perder la comunicación o con falla del sensor. La purga tiene prioridad. Si la válvula queda abierta más que el tiempo máximo (por ejemplo, una descarga tapada), se cierra y se cancela.
  - La presión fijada debe quedar bajo la de purga.
  - En la interfaz: campo, botones "Fijar" y "Cancelar", estado y una línea punteada verde en el gráfico.
- **Probado en modo demo:** desde 1,08 bar sin carga, fijada en 0,60 bar, llegó a 0,61. Con la carga del simulador encendida (0,12 bar/s), se mantuvo entre 0,62 y 0,75 bar abriendo cada ~1 s.
- **Por ajustar en el banco real:** la banda (0,05), el anticipo (0,02) y la espera (1 s) son valores iniciales. Dependen de cuánto tarda en descargar el tanque real. Con el compresor conectado, mantener la presión hace que la válvula conmute seguido; conviene cortar la carga antes de fijar.
- Sintaxis del firmware revisada de nuevo con sustitutos de las bibliotecas; sigue **sin compilar para ESP32 ni probar en el hardware**.
