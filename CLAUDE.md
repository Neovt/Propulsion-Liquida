# CLAUDE.md — Proyecto de propulsión líquida IGNIS

Contexto para Claude al trabajar en este repositorio. El proyecto es del Grupo de Interés en Propulsión (GIP), Universidad de Concepción, Chile. Los documentos están en español; mantén ese idioma en la documentación y en los comentarios.

## Qué es el proyecto

IGNIS es un banco de ensayos de propulsión con **queroseno** y **oxígeno gaseoso (GOX)**. Es un sistema **bipropelente líquido–gas**. La arquitectura original (Memoria de Cálculo V0) usaba peróxido de hidrógeno al 50 % e isopropanol, con una cámara de 10 bar absolutos. Se cambió a queroseno y GOX por disponibilidad, manipulación, costo y complejidad experimental. Nitrógeno (N2) se usa para presurización y purga.

El desarrollo es incremental: la maduración se divide en fases, y la transición a la siguiente exige verificar y documentar el avance (metodología basada en INCOSE SE Handbook).

## Fases

- **Fase 1 (activa)**: definición y verificación del sistema de fluidos, presurización y control. Pruebas en frío con agua, aire, N2 y queroseno. Usa tanques extintores disponibles y luego recipientes sustitutos para mayor presión. El uso de oxígeno es un extra de la campaña, condicionado a preparación y compatibilidad.
- **Fase 2**: placa inyectora definitiva (patrón tipo shower para GOX alrededor del inyector central de queroseno), alojamiento dual, stand de alta presión y encendidos abiertos sin tobera.
- **Fase 3**: cámara de combustión confinada, análisis termodinámico, transferencia de calor, tobera De Laval. Objetivo preliminar de cámara: 10 bar.

Fuera de alcance de Fase 1: diseño definitivo de la placa, stand de encendido y evaluación de combustión. No se mezclan deliberadamente GOX y queroseno en pruebas en frío.

## Documentos de referencia

- `docs/IGNIS_Fase1_Rev1.1.pdf`: documento oficial de Fase 1, revisión 1.1 (2026). Es la fuente principal de requisitos y de la descripción del P&ID.
- Registro de Fase 1 de selección de electrónica (proyecto de Claude): ver sección "Electrónica" más abajo.
- Registro de piezas provisorias impresas (proyecto de Claude): ver sección "Piezas" más abajo.

Si estas instrucciones y el PDF se contradicen, prevalece el PDF y se debe avisar.

## Requisitos clave (resumen del PDF)

**Alimentación**
- Combustible impulsado con N2 sobre el espacio gaseoso del recipiente, por diferencia de presión (tubo sifón).
- Alimentación preliminar 38–40 bar. Cámara futura ~10 bar absolutos. Estas cifras son estimaciones a verificar.
- En Fase 1, las descargas abiertas están esencialmente a presión atmosférica.
- Cilindro N2 de alta presión, referencia 150 bar, conexión CGA-580.

**Recipientes**
- Extintores disponibles: presión de trabajo ~15 atm, presión de ensayo grabada 31 atm técnicas. Cada recipiente conserva su identificación y su marca de ensayo.
- La presión de ensayo no es de uso continuo. Los extintores no cubren todo el rango previsto: deben sustituirse por recipientes aptos para fluido, temperatura y presión antes de superar sus límites.
- Tapón propuesto: exterior M24×1,5 con puerto 1/8 NPT hembra. Se verifica contra el cuello del extintor.

**Interfaces**
- Se deben integrar conexiones NPT, BSPP, BSPT y AN. Identificar familia, tamaño, asiento y sello.
- BSPP usa el sello previsto para su asiento (arandelas y/u o-rings).
- Sellantes (PTFE, FKM/Viton, Loctite 542/567, Krytox GPL 205) se eligen por especificación, fluido y condiciones.

**GOX**
- Requiere limpieza y compatibilidad del conjunto. Un color de cinta o un nombre comercial no demuestran aptitud para oxígeno. Referencia: NASA/TM-2007-213740.
- El circuito GOX se mantiene separado de contaminación por combustible y aceites.
- Preliminar: CGA-540, suministro 150 bar, regulación 20–25 bar, mangueras PTFE, electroválvula de orificio 5 mm.
- Pruebas con otros medios no habilitan el uso con GOX. Se requieren pruebas exclusivas de oxígeno.

**Instrumentación y control**
- Adquisición continua y sincronizada de presiones, con marca de tiempo de alta resolución.
- Electroválvulas manejadas por el sistema de control, con arquitectura a prueba de fallos: la pérdida de energía eléctrica o de comunicación devuelve los actuadores a su estado seguro de reposo.

**Circuitos del P&ID (Figura 1 del PDF)**
- Rama N2: cilindro → regulación y transductor de presión → distribución N2 → solenoides y línea de purga; de ahí presurización del tanque de líquido.
- Rama líquido: tanque de líquido → solenoides y control → inyector o descarga. Agua o queroseno según la campaña.
- Rama GOX: cilindro → regulación y transductor → solenoide → manguera → check y salida. Se mantiene separada de la descarga de combustible.
- Purga: inyectar N2 a alta presión para eliminar el residual de queroseno del inyector y las válvulas.
- Válvulas check limitan el retorno. Su sentido y presión de apertura forman parte de la selección.

**Inyector**
- Inyector de turbina Allison 250-C20B (referencia de la memoria de Aarón Espinoza Barreiro, 2026). Gotas predichas de ~152–166 µm en 26–30 bar, por modelo de ruptura primaria, no por medición directa.
- Objetivo: conservar una caída de presión elevada en el inyector.

**Hitos (Tabla 1 del PDF)**
- R-01: documento validado por pares.
- R-02: ensamble en seco (dry-fit) del prototanque.
- R-03: hermeticidad y control de válvulas por electrónica.
- R-04: estanqueidad a baja presión con adquisición de datos y control de válvulas.
- R-05: carga, presurización y descarga completadas de forma segura y repetible.

**Zonas de ensayo**
- Espacio abierto exterior del Laboratorio de Técnicas Aeroespaciales. Para alta presión se evalúa un container.

## Electrónica (Fase 1)

Comprado:
- Válvula solenoide JT22-02, 1/4" BSPP, latón, NC, FKM, 12 V DC, orificio 5 mm, 0–80 bar (según anuncio).
- Driver DRV8871 (1 canal, 6,5–45 V, límite 3,6 A).

Seleccionado / por comprar:
- Transductor Veto C9044528 (4–20 mA, 2 hilos, 12–36 V, ±0,5 % FS, 1/2" NPT).
- Conversión 4–20 mA a voltaje: DFRobot Gravity SEN0262 (0–25 mA → 0–3 V, alimentación 3,3–5,5 V), hacia el ADC del GIP.
- Alimentación: fuente 12 V (válvula) y fuente 24 V aparte (lazo del transmisor), GND común.
- Opcional: INA219 en serie con +12 V antes del DRV8871 (máx. ~3,2 A).
- Plan B de driver si la bobina supera ~2–3 A: módulo MOSFET DC 3.7–27 V con diodo SR5200 en paralelo con la bobina (banda al lado positivo).

Pendientes de verificar:
1. Potencia y corriente de la bobina de 12 V. Regla: ≤ ~15 W conviene DRV8871; más, MOSFET + diodo.
2. Presión mínima de apertura (probablemente asistida por diafragma). Probar con aire a 0,5 / 1 / 2 bar antes de usar N2.
3. Resistencia ILIM del DRV8871 (limita corriente de arranque).
4. Rango del transmisor Veto: 25 bar FS para extintores; 60 bar FS para 40 bar finales.
5. Cableado exacto del SEN0262 según su wiki.
6. **La válvula (latón + FKM) NO está calificada para GOX.** Solo agua, aire, N2 y queroseno.

Control: abrir con IN1 alto e IN2 bajo. Cerrar o estado seguro con ambas bajas. Sin PWM para abrir; PWM de mantención 40–60 % opcional después de abrir.

## Piezas impresas provisorias (proto-tanque)

Uso: pruebas de telemetría con aire o agua a baja presión (máximo absoluto 8 bar), mientras llegan el adaptador M30 metálico y el tubo sifón.

- **P1, adaptador cuello M30×1,5 → R1/4 BSPT**: M30×1,5 macho, 12 mm de rosca, holgura −0,3 mm en diámetro. Sello con o-ring 31×2 en glándula triangular de 45° (estilo válvula original de extintor). Hexágono de 40 mm entre caras. R1/4 BSPT macho de 10 mm (conicidad 1:16, −0,2 mm en diámetro). Agujero pasante de 4 mm. ~31 g en PETG.
- **P2, niple R1/4 BSPT – R1/4 BSPT (cruz → solenoide JT22-02)**: doble macho cónico, 10 mm de rosca por lado, hexágono de 17 mm, agujero de 4 mm. ~5 g. Sella con teflón contra hembras BSPP.
- Impresión: PETG, boquilla 0,4, eje vertical (P1 con la M30 sobre la cama), capa ≤ 0,12 mm, relleno 100 %, ≥ 5 perímetros.
- Pendiente de medir: diámetro exterior de la cara superior del cuello (≥ ~38 mm para el tope), profundidad de rosca del cuello (≥ 12 mm) y medida real del o-ring disponible.
- Script paramétrico `piezas/generar_piezas.py` (numpy) genera los STL, que también están en `piezas/`.

## Bitácora de avances

El avance del proyecto se acumula en `docs/bitacora/`, como un historial largo y secuencial.

- **Un archivo por avance**: `docs/bitacora/AAAA-MM-DD_tema.md`. Nunca se sobrescribe una entrada anterior; las correcciones van en una entrada nueva o en una sección de fe de erratas que cite la original.
- **Extensas y con contexto**: una persona que no vio la conversación debe poder entender qué se hizo, por qué y con qué resultado.
- **Por bloques, en orden cronológico**: objetivo y contexto, lo que se hizo paso a paso, mediciones y resultados con valores y unidades, problemas y correcciones, pendientes, archivos asociados.
- Distinguir lo medido o verificado de lo supuesto o estimado, y decirlo explícitamente.
- Cada entrada nueva se agrega al índice de `docs/bitacora/README.md`.
- El código va en `firmware/` y las piezas (STL y generadores) en `piezas/`; las bitácoras los enlazan con rutas relativas y no los duplican.
- Cada entrada lleva el bloque de firma descrito a continuación.

## Firma de autoría en los documentos Markdown

Todo `.md` que Claude cree o modifique de forma sustancial en este repositorio (bitácoras, registros, notas técnicas) lleva, justo debajo del título, un bloque de firma para saber quién trabajó en él:

```
> **Autoría:** <nombre de la persona> (<usuario de GitHub>)
> **Redacción asistida por:** Claude (<modelo>)
> **Fecha:** AAAA-MM-DD · **Estado:** borrador | revisado
```

- **Autoría** es la persona que dirige el trabajo en la conversación, con su usuario de GitHub si lo indicó. Si no se sabe quién es, Claude lo pregunta; no inventa nombres ni firma a nombre de otra persona.
- **Redacción asistida por** indica el modelo de Claude que escribió el texto. Si intervinieron varios, se listan todos.
- **Estado** es `borrador` mientras nadie del equipo haya revisado el contenido. Solo la persona autora lo cambia a `revisado`.
- Cuando otra persona edite un documento firmado, añade su propia línea `**Editado por:**` con la fecha; no se reemplaza la autoría original.
- En los mensajes de commit no se escriben menciones con arroba, para no notificar a nadie sin querer.

## Reglas de trabajo para Claude

- No presentes como verificadas las cifras marcadas como estimaciones (38–40 bar, 150 bar, 10 bar, etc.).
- No recomiendes ni documentes uso de GOX con componentes no calificados (latón, FKM, sellantes no especificados para oxígeno). Remite a la compatibilidad de NASA/TM-2007-213740.
- Mantén la separación de circuitos GOX y queroseno en cualquier diagrama o código.
- Cuando cambies un componente, actualiza el P&ID y las comprobaciones (según sección 3.2 del PDF).
- Los cambios de fluido y de presión se validan por separado; una prueba de estanqueidad con un fluido no acredita compatibilidad con otro.
- Documentos y código en español.
