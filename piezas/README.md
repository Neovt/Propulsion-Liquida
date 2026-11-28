# Piezas — IGNIS

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-27 · **Estado:** borrador

Archivos de fabricación (STL), generadores paramétricos y scripts de Fusion. Las versiones anteriores se conservan para que las bitácoras sigan enlazando a lo que se describió en su momento. **La versión vigente de cada pieza está marcada abajo.**

## Proto-tanque (piezas impresas provisorias, máx. 8 bar)

| Archivo | Pieza | Estado |
|---|---|---|
| [`P1_adaptador_M30_R14.stl`](P1_adaptador_M30_R14.stl) | Adaptador del cuello M30×1,5 → R1/4 BSPT, sello con o-ring 31×2 | Diseñado; uso pendiente |
| [`P2_niple_R14_R14.stl`](P2_niple_R14_R14.stl) | Niple R1/4 BSPT macho–macho (cruz → solenoide) | **En uso.** Reimpreso más macizo en PETG para la prueba del 27-11; sin fugas hasta ~1,8 bar |
| [`generar_piezas.py`](generar_piezas.py) | Generador paramétrico de P1 y P2 (numpy) | — |

La versión más maciza de P2 que se usó el 27-11 se preparó fuera de este repositorio. Conviene subir aquí su STL o sus parámetros.

## Inyector impreso de prueba (PETG)

| Archivo | Estado |
|---|---|
| [`inyector_impreso/`](inyector_impreso/), [`generar_inyector.py`](generar_inyector.py), [`calculo_inyector.py`](calculo_inyector.py) | Swirl R1/4 BSPT, hex 17, para probar en el banco; ver la bitácora del 26-11 |

## Elemento inyector CNC (queroseno, swirl simplex, compatible con el banco del Allison 250)

| Carpeta | Estado |
|---|---|
| [`elemento_inyector_v5/`](elemento_inyector_v5/) | **Vigente.** Brida de la punta Ø26 que cubre la arandela de cobre; 15 g/s a 7,5 bar (teórico); herramienta mínima Ø2 |
| [`elemento_inyector_v4/`](elemento_inyector_v4/) | Superada por v5. Entrada macho M12×1,5 24°, sellos de cobre |
| [`elemento_inyector_v3/`](elemento_inyector_v3/) | Superada. Tenía la entrada hembra y una ranura sin sellar |
| [`mini_motor_v3/`](mini_motor_v3/) | Parámetros del bosquejo de motor v3. El bosquejo vigente lo genera el script de v5 |

Cada carpeta del elemento contiene:
- `geom_vN.py`: geometría;
- `calculo_vN.py`: caudal y calibración;
- `verificar_vN.py`: verificación independiente por vóxeles;
- `plantilla_vN.py` y `fusion/`: script para generar el modelo en Fusion.
