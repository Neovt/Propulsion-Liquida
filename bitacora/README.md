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

## Cómo agregar una entrada

1. Crear `AAAA-MM-DD_tema.md` en esta carpeta, con el bloque de firma descrito en `CLAUDE.md`.
2. Añadir una fila al índice de arriba.
3. Si hay código o piezas nuevas, guardarlas en `codigos/` o `piezas/` y enlazarlas desde la entrada.
