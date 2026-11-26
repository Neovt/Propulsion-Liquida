# Inyector propio: de la pieza impresa al elemento CNC v3, datos del Allison 250 y mini motor

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5, Opus 5.5)
> **Fecha:** 2026-11-26 · **Estado:** borrador

Entrada que cubre las sesiones del 25 y 26 de noviembre de 2026. En la tabla de abajo se distingue lo **verificado** (medido, comprobado en el modelo o leído de archivos) de lo **estimado** (cálculo de diseño sin ensayo). Ninguna pieza de esta entrada se ha fabricado ni ensayado todavía.

| Tipo de dato | Ejemplos en esta entrada |
|---|---|
| Verificado | geometría interna del Allison 250 leída del modelo CFD de A. Espinoza; caudal CFD del Allison (27,8 g/s a 5 bar); conectividad, paredes e interferencias de los modelos 3D |
| Estimado | caudales, ángulos de cono, tamaño de gota, presiones de cámara, empuje y temperaturas de todo diseño propio |

---

## 1. Objetivo

Diseñar un **inyector propio que sea un elemento**: una pieza autónoma, como el Allison 250-C20B, que se pueda ensayar sola en el banco de inyectores y luego montar en una placa y en un motor pequeño. Las condiciones de partida son:

- **Presión disponible:** la del prototanque actual, 8 bar seguros y 10 bar como máximo eventual.
- **Fabricación:** CNC y torno del laboratorio, con un límite estricto de herramienta.
- **Compatibilidad:** la mayor posible con el banco y con el Allison.

## 2. Transmisor de presión (preparación de la prueba)

- Montaje: XDB401 (0–40 bar, 0,5–4,5 V, alimentado a 12 V) → ADS1115 a 5 V, ganancia ±6,144 V → ESP32 por I²C.
- Código: [`../codigos/presion/presion.ino`](../codigos/presion/presion.ino). Entrega un CSV `t_ms,volts,bar` y acepta los comandos `zero` y `reset`. Marca falla si la lectura está bajo 0,4 V o sobre 4,6 V. **Sin probar.**
- Plan de prueba acordado:
  1. Continuidad de GND entre el driver, la fuente y el ESP32.
  2. Unos 0,5 V en el cable amarillo con el tanque abierto.
  3. Comando `zero` a presión atmosférica.
  4. Presión de aire en escalones de hasta 3 bar.
  5. Revisar fugas con agua jabonosa y ruido al conmutar la solenoide.
- Error esperable: ±0,5 % FS, es decir ±0,2 bar. La calibración de span es opcional; basta comparar con un manómetro a unos 2 bar. El transmisor se alimenta a 12 V y su salida no depende del rail de 5 V.

## 3. Inyector impreso de prueba (PETG)

- Rosca R1/4 BSPT macho (sella con teflón en la salida BSPP de la solenoide), hexágono de 17 y descarga axial.
- Interior swirl:
  - 4 canales llevan el líquido a 4 puertos tangenciales;
  - una cámara de remolino Ø6 y un cono de 90° terminan en el orificio de salida;
  - hay una familia de orificios de Ø1,5 / 2,0 / 2,5 / 3,0 mm más un orificio recto de referencia Ø2,0.
- Estimaciones con la teoría de Abramovich (A = 1,7, μ ≈ 0,32, cono ≈ 80°): la versión Ø2,0 da unos 20 mL/s de agua a 2 bar.
- Verificado en el modelo: el canal es continuo, la malla es hermética y el orificio de la malla mide Ø1,999 mm.
- Para empezar se recomienda imprimir la Ø2,0.
- Archivos: [`../piezas/generar_inyector.py`](../piezas/generar_inyector.py), [`../piezas/calculo_inyector.py`](../piezas/calculo_inyector.py), [`../piezas/inyector_impreso/`](../piezas/inyector_impreso/) (STL Ø2,0 swirl y orificio recto).

## 4. Iteraciones CNC v1–v2 y primer mini motor (descartados)

- **Inyector coaxial v1–v2:** sirvieron para fijar reglas de diseño que siguen vigentes:
  - las roscas BSPP sellan con arandela contra una **cara plana**, no por la rosca;
  - los tornillos van **ciegos**, nunca abiertos hacia la llama;
  - los bordes entre ranuras de o-ring deben medir 2 mm o más;
  - la entrada de gas debe tener otro tamaño que la de líquido, para que no se puedan intercambiar las mangueras.
- **Mini motor v1:** era una cabeza de inyección completa en la que "todo era inyector". Matías lo objetó con razón: el objetivo es un **elemento** autónomo. Se descartó.
- Aclaración: las cifras del motor v1 (Pc 5 bar, encendidos de 5 s) son elecciones propias del cálculo, no de la Memoria de Cálculo V0, a la que no se tuvo acceso. El parecido con el prediseño del motor completo de hace seis meses es coincidencia.

## 5. Datos del Allison 250-C20B (de los archivos de A. Espinoza)

- **Fuente:** carpeta `Inyector Alisson250_files` (proyecto ANSYS Workbench).
  - La geometría venía en un documento SpaceClaim con dos Parasolid. Se subieron a Fusion para medirlos y quedaron en `GIP > Proyecto_liquido`.
  - Los resultados de Fluent vienen en el archivo de interpolación `FLTG.ip`.
- **Los archivos solo contienen el volumen de fluido.** El cuerpo exterior (roscas, hexágono, asiento) **no está**; hay que medirlo en la pieza real.
- **Geometría interna medida** (Fusion API, [`../docs/allison250/medidas_fluido_allison250.txt`](../docs/allison250/medidas_fluido_allison250.txt); z = 0 en la entrada):

| Zona | Medida |
|---|---|
| Entrada | Ø4,1 × 1,3 |
| Filtro | Ø6,15, z 1,9–13,1 (cuerpo poroso Ø3,6) |
| Válvula | Ø4, z 14–23, con agujero transversal Ø1,6 |
| Cavidad del cuerpo | Ø11,85, z 21–37,9 (anillo hasta Ø9) |
| Primario | 4 agujeros axiales Ø0,85 → cámara de remolino Ø4,35 con 2 entradas tangenciales Ø0,5 → orificio Ø0,95 (z 39,1–40,9) |
| Secundario | 6 agujeros Ø1,0 inclinados → anillo de remolino Ø10 → salida anular alrededor del primario (Ø1,5–Ø2,0) |
| Salida | a **40,9 mm** de la entrada |

- **CFD** (k-ε, entrada 5 bar, salida 0 bar): **27,8 g/s**, velocidad de salida unos 20,9 m/s.
- Cortes del dominio de fluido: [`../docs/allison250/cortes_fluido_allison250.png`](../docs/allison250/cortes_fluido_allison250.png).

## 6. Elemento inyector v3 (diseño actual)

### 6.1 Reglas de diseño

- **Ninguna broca ni fresa menor que Ø2,0 mm.** El taller no tiene herramienta fina y no se trabaja al límite de la máquina.
- Swirl simplex **solo de queroseno**. El GOX lo pone la placa, como en el concepto de la Fase 2 con el Allison al centro. El elemento no toca oxígeno por dentro.
- Se arma una vez y no se vuelve a desarmar, pero es desarmable para poder montarlo e inspeccionarlo.

### 6.2 Camino del combustible

1. Entrada **G1/4 hembra** atrás (racor recto G1/4 – tubo 6 mm del banco).
2. Paso axial Ø6.
3. Cámara de reparto Ø12,4 × 1,5.
4. **3 agujeros axiales Ø2** en el remolinador (r = 5).
5. **3 ranuras tangenciales 2,0 × 0,75** (fresa Ø2), tangentes a la pared de la cámara. Aquí nace el giro.
6. **Cámara de remolino Ø7 × 4** (en la punta).
7. Cono de 90°.
8. **Orificio Ø2,0 × 1,5**, del que sale el cono hueco.

### 6.3 Piezas

| Pieza | Material | Descripción |
|---|---|---|
| Cuerpo | inox 303/316 | hexágono 27; hombro de sello; **M24×1,5** de montaje; frente liso Ø22; rosca interior M18×1,5; asiento del remolinador (anillo Ø12,4–Ø14) |
| Remolinador | inox | Ø14 H7/g6 × 6, chaflán trasero 0,3, 3 agujeros Ø2, 3 ranuras 2 × 0,75 |
| Punta | inox | M18×1,5 exterior; brida Ø22 con planos de llave 19; cámara Ø7, cono 90°, orificio Ø2. **Aprieta solo el remolinador**: queda un juego de 0,5 mm entre la brida y el cuerpo, para que el apriete no quede sobredeterminado |
| Arandela | cobre | DIN 7603 A 24×30×2, entre el hombro y la placa |
| Alambre de seguridad | — | agujeros Ø2 en una esquina del hexágono y en una cuerda de la brida (no tocan la cámara) |

### 6.4 Verificado en los modelos

- Modelo de vóxeles independiente ([`../piezas/elemento_inyector_v3/verificar_v3.py`](../piezas/elemento_inyector_v3/verificar_v3.py)):
  - el canal entrada → orificio es continuo;
  - **sin las ranuras el canal queda cortado**, así que todo el combustible gira;
  - no hay interferencias;
  - las paredes mínimas son: cuerpo 2,8 mm, punta 2,5 mm, remolinador 1,0 mm.
- Fusion (script v3): sin interferencias inesperadas y roscas cosméticas G1/4, M24, M18 y G1/8 aplicadas. El corte XZ se revisó visualmente.
- Corrección durante el diseño: con la cámara de Ø8, los agujeros axiales quedaban 0,2 mm dentro de la huella de la cámara (bypass sin giro). Se redujo la cámara a Ø7 y quedó 0,5 mm de margen.

### 6.5 Estimaciones hidráulicas (Abramovich + correlación de Lefebvre para el tamaño de gota)

A = 1,745, μ ≈ 0,316, cono ≈ 82° total.

| ΔP | Agua | Queroseno | Tamaño de gota (SMD) queroseno |
|---|---|---|---|
| 2 bar | 19,8 g/s | 17,7 g/s | ≈ 100 µm |
| 3,5 bar | 26,2 g/s | 23,5 g/s | ≈ 81 µm |
| 5 bar | **31,3 g/s** | 28,0 g/s | ≈ 71 µm |
| 8 bar | 39,6 g/s | 35,5 g/s | ≈ 59 µm |

A 5 bar está en la **misma clase de caudal que el Allison** (27,8 g/s en CFD), así que ambos se pueden comparar en el mismo banco.

### 6.6 Fabricación, armado e instalación

- **Fabricación:**
  - Cuerpo: torno en dos amarres (atrás: hexágono y G1/4; adelante: M24, frente, alojamiento Ø14 H7 y rosca M18).
  - Remolinador: torno y luego fresa Ø2 para las ranuras.
  - Punta: torno en un solo amarre para la cámara, el cono y el orificio, y así asegurar la concentricidad.
  - Sin rebabas en el orificio, las ranuras y los agujeros.
- **Armado:** remolinador en su asiento, punta apretada a mano firme con llave 19, alambre de seguridad.
- **Instalación en el banco:** soporte con agujero M24×1,5 (incluido en el modelo), racor G1/4 – tubo 6 mm.
- **Instalación en la placa:** se atornilla desde atrás en una rosca M24×1,5 con arandela de cobre. El frente Ø22 pasa a ras de la cara.
- **Compatibilidad física con el Allison:** pendiente. Requiere medir su rosca de montaje, el hexágono, el asiento y la posición de la punta. Si hace falta, se cambian el M24, el hexágono o los largos; el interior no cambia.

## 7. Mini motor v3 (bosquejo de integración)

Dimensionado para el elemento v3 y el prototanque. **Todo estimado.**

| Magnitud | Valor |
|---|---|
| Tanque de combustible | 8 bar man. (N2 regulado) |
| Pérdidas de línea | 0,5 bar (supuesto) |
| ΔP en el inyector | 3,5 bar |
| Presión de cámara | ≈ 5,1 bar abs |
| Queroseno | 23,5 g/s (29 mL/s) |
| GOX (O/F 2,2) | 51,7 g/s |
| Garganta | Ø17 |
| Cámara | Ø56 interior × 92 mm (contracción 10,9, L* ≈ 1,2 m) |
| Salida de tobera | Ø20,5 (ε 1,47) |
| Empuje | ≈ 120 N |
| GOX por la placa | 7 agujeros **Ø2** inclinados 20° hacia el eje, flujo bloqueado con 11,8 bar abs en el colector |
| Solenoide GOX Ø5 con regulador a 20 bar | ≈ 61 g/s de capacidad, con poco margen |

- **Piezas:**
  - colector de GOX (entrada lateral G1/4 sobre cara de asiento, o-rings 26×2 y 45×2, rosca M24 para el elemento);
  - placa inyectora (Ø110, roscas M5 ciegas, ranura de junta);
  - juntas de grafito;
  - cámara de inox Ø70/Ø56 con dos puertos G1/8;
  - tobera de **cobre** con brida;
  - 4 varillas M8 por fuera de la cámara;
  - 3 tornillos M5×14.
- **Térmico** (orden de magnitud): la garganta de cobre sube unos 214 K en 3 s; una de inox subiría unos 977 K. Encendidos de 2–3 s.
- **Consumo:** 2 L de queroseno alcanzan para unos 68 s de flujo. Un encendido de 3 s gasta unos 88 mL de queroseno y 155 g de GOX.

## 8. Problemas y correcciones

- El PDF de la memoria de A. Espinoza subido el 26-11 era una página HTML de descarga, no el documento. Se usaron en cambio los archivos de su proyecto ANSYS.
- Los Parasolid del Allison se subieron primero a la raíz del proyecto GIP de Fusion, que no es nuestra nube, y luego **se movieron a `Proyecto_liquido`**. La raíz quedó solo con las carpetas.
- Se abrió por error una segunda instancia de Fusion; se cerró desde el Administrador de tareas y se perdieron documentos sin guardar de iteraciones anteriores. Todos se regeneran con sus scripts.
- La punta v2 tenía los planos de llave sobre la rosca interior, con una pared de 0,56 mm; en la v3 no ocurre.

## 9. Pendientes

1. **Medir el Allison real** (rosca y asiento de montaje, hexágono, posición de la punta, conexión del capilar) y ajustar la interfaz del elemento.
2. Confirmar con el taller la broca y la fresa mínimas (se asumió Ø2) y el inclinado de 20° de los agujeros de GOX.
3. Fabricar el elemento v3 en latón para agua y aire; caracterizar el caudal contra ΔP (Cd real), el ángulo del cono y la simetría con un patternator simple.
4. Probar el transmisor (sección 2) y subir los datos.
5. Para cualquier uso con GOX: materiales, elastómeros y limpieza según NASA/TM-2007-213740. La JT22-02 no sirve para GOX.
6. Imprimir y ensayar el inyector impreso Ø2,0.

## 10. Archivos

- [`../piezas/elemento_inyector_v3/`](../piezas/elemento_inyector_v3/): `geom_v3.py` (cotas), `calculo_v3.py` (hidráulica y motor), `verificar_v3.py` (verificación independiente), `plantilla_v3.py` y `fusion/` (script de Fusion que genera el elemento, el soporte de banco y el mini motor).
- [`../piezas/mini_motor_v3/motor_v3.json`](../piezas/mini_motor_v3/motor_v3.json): contorno de tobera y cotas del motor.
- [`../piezas/generar_inyector.py`](../piezas/generar_inyector.py), [`../piezas/calculo_inyector.py`](../piezas/calculo_inyector.py), [`../piezas/inyector_impreso/`](../piezas/inyector_impreso/): inyector impreso.
- [`../docs/allison250/`](../docs/allison250/): medidas del fluido, cortes y el script de medición de Fusion.
- [`../codigos/presion/presion.ino`](../codigos/presion/presion.ino): lectura del transmisor.
- En Fusion (`GIP > Proyecto_liquido`): "IGNIS Elemento inyector swirl v3", "IGNIS Mini motor v3 (bosquejo)", `Allison250_part1bodies`, `Allison250_part2bodies`.
