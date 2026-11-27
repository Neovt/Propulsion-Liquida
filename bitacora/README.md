# Bitácora de avances — IGNIS

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5)
> **Fecha:** 2026-11-21 · **Estado:** borrador

Historial acumulado del trabajo del proyecto. Cada avance es un archivo propio, con la fecha al inicio del nombre (`AAAA-MM-DD_tema.md`), de modo que el orden alfabético es el orden cronológico. Las entradas no se sobrescriben: el historial solo crece. Si algo resulta ser un error, se corrige en una entrada nueva o en una sección de fe de erratas, citando la entrada original.

Código y archivos de fabricación viven fuera de las bitácoras y se referencian con rutas relativas: `../piezas/` (STL y generador) y `../codigos/` (sketches y programas).

## Índice

| Fecha | Entrada | Resumen | Estado |
|---|---|---|---|
| 2026-11-21 | [Solenoide, driver y ESP32](2026-11-21_solenoide_driver_esp32.md) | Revisión del proto-tanque y compras, piezas impresas P1/P2, cableado de la solenoide JT22-02, driver DRV8871 con ESP32, problemas resueltos (puerto COM, fuente en CC, PWM de mantención) | borrador |
| 2026-11-26 | [Inyector elemento y mini motor](2026-11-26_inyector_elemento_y_mini_motor.md) | Plan de prueba del transmisor, inyector impreso PETG, datos internos del Allison 250 (CFD de A. Espinoza), elemento inyector CNC v3 (herramienta mínima Ø2) y bosquejo de mini motor | borrador |
| 2026-11-26 | [Elemento inyector v4 y fe de erratas](2026-11-26_elemento_inyector_v4.md) | Corrige el caudal del Allison (ensayo: ~14 g/s a 14 bar), entrada macho M12x1,5 24°, sellos de cobre sin ranuras, 15 g/s a 7,5 bar con herramienta mínima Ø2 y remolinadores de calibración | borrador |
| 2026-11-26 | [Elemento inyector v5](2026-11-26_elemento_inyector_v5.md) | Brida de la punta Ø26 que tapa la arandela de cobre; sin agujeros de alambre de seguridad; cámara del bosquejo sin puertos laterales | borrador |
| 2026-11-26 | [Primera prueba del transmisor de presión](2026-11-26_transmisor_presion_prueba.md) | Montaje y prueba del XDB401 con ADS1115 a presión atmosférica; el desfase de 0,15 V se debía a que el cable estaba soldado en A1 y el código leía A0; estimación de consumo en los 12 V; pendientes de la prueba con presión | borrador |
| 2026-11-27 | [Interfaz del banco de ensayo](2026-11-27_interfaz_banco.md) | Programa único del ESP32 (presión a 20 Hz + válvula con seguridad local: cierre por pérdida de comunicación y purga por sobrepresión) e interfaz HTML en Chrome con gráfico y grabación a CSV | borrador |
| 2026-11-27 | [Primera prueba integrada del banco](2026-11-27_primera_prueba_integrada.md) | Compresor + transmisor + solenoide + interfaz, hasta ~1,8 bar; fallas de cableado resueltas (SCL desoldado, cable del driver cortado por dentro); fuga cerca de la válvula de bola sobre 1,4 bar; desconexiones del ESP32 al arrancar el compresor; mejoras propuestas | borrador |

## Cómo agregar una entrada

1. Crear `AAAA-MM-DD_tema.md` en esta carpeta, con el bloque de firma descrito en `CLAUDE.md`.
2. Añadir una fila al índice de arriba.
3. Si hay código o piezas nuevas, guardarlas en `codigos/` o `piezas/` y enlazarlas desde la entrada.
