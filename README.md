# IGNIS — Banco de ensayos de propulsión líquida

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-27 · **Estado:** borrador

Proyecto del **Grupo de Interés en Propulsión (GIP)** de la Universidad de Concepción, Chile. IGNIS es un banco de ensayos bipropelente de **queroseno** y **oxígeno gaseoso (GOX)**, presurizado con nitrógeno. El desarrollo va por fases; hoy está activa la **Fase 1**: sistema de fluidos, presurización y control, con pruebas en frío (agua, aire, N₂ y queroseno).

El documento oficial de la Fase 1 es [`docs/IGNIS_Fase1_Rev1.1.pdf`](docs/IGNIS_Fase1_Rev1.1.pdf). Las reglas de trabajo del repositorio están en [`CLAUDE.md`](CLAUDE.md).

## Estructura

| Carpeta | Contenido |
|---|---|
| [`bitacora/`](bitacora/README.md) | Historial del proyecto: una entrada por avance, en orden cronológico. **Empieza aquí.** |
| [`codigos/`](codigos/README.md) | Programas del ESP32 y la interfaz del banco |
| [`piezas/`](piezas/README.md) | Piezas impresas, generadores y scripts de Fusion del elemento inyector |
| [`docs/`](docs/) | Documento de la Fase 1 y datos del inyector Allison 250 |

## Estado actual (2026-11-27)

| Sistema | Versión vigente | Estado |
|---|---|---|
| Banco: firmware del ESP32 | [`codigos/banco/banco.ino`](codigos/banco/banco.ino) v3 | La v2 se probó integrada con aire hasta ~1,8 bar; la v3 está revisada en sintaxis y sin probar en el hardware |
| Banco: interfaz | [`codigos/interfaz/banco.html`](codigos/interfaz/banco.html) | Probada con el banco real (v2) y en modo demo (v3) |
| Proto-tanque | Extintor + cruz 1/4" + adaptador P2 impreso en PETG | Hermético en P2; fuga en la llave de entrada sobre ~1,4 bar |
| Elemento inyector CNC | [`piezas/elemento_inyector_v5/`](piezas/elemento_inyector_v5/) | Diseñado y verificado en el modelo; sin fabricar |

## Seguridad

- La solenoide JT22-02 (latón + FKM) y el resto de los componentes actuales **no están calificados para GOX**. Solo agua, aire, N₂ y queroseno. La compatibilidad con oxígeno se rige por NASA/TM-2007-213740.
- Las piezas impresas son provisorias: **máximo absoluto de 8 bar**, y la primera presurización con agua.
- Las cifras de presión del proyecto (38–40 bar de alimentación, 10 bar de cámara) son **estimaciones por verificar**.
