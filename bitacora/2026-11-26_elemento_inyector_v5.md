# Elemento inyector v5: brida que tapa el sello, sin agujeros innecesarios

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-26 · **Estado:** borrador

Continúa [la entrada del v4](2026-11-26_elemento_inyector_v4.md). La hidráulica no cambia: remolinador, cámara de remolino y orificio son idénticos al v4, con 15,1 g/s teóricos a 7,5 bar.

## 1. Observaciones de Matías sobre el v4

1. **La arandela de cobre de la punta quedaba expuesta.** La brida de la punta (Ø22) tenía el mismo diámetro que la arandela (Ø22). Desde la cámara se veía el borde del sello a 2,5 mm de la cara de salida. En quemas de minutos, los gases recirculados lo calentarían, y detrás está el combustible a presión. Matías pidió **ensanchar** la punta, no alargarla, para que la propia cara de salida cubra el sello.
2. **Agujero horizontal sin conexión en la punta.** Era un agujero de Ø2 para alambre de seguridad (lockwire). En el motor queda dentro de la placa, así que no se puede usar, y además está en el lado caliente. El del hexágono del cuerpo tampoco aporta por ahora.
3. **Dos puertos laterales en la cámara.** Eran dos G1/8 con paso Ø2: uno para la toma de presión y otro para el encendedor (este último, además, mal dimensionado). Matías decidió **no poner ninguno todavía**.

## 2. Cambios del v5

| Pieza | v4 | v5 |
|---|---|---|
| Brida de la punta | Ø22, planos de llave 19 | **Ø26, planos de llave 24**: la cara cubre por completo la arandela Ø18,5/22 (los planos quedan a 12 mm del eje, fuera del borde de 11 mm de la arandela) |
| Alambre de seguridad | punta y hexágono del cuerpo | **eliminado en ambos**; la punta queda fija por torque y arandela de cobre |
| Cámara (bosquejo) | 2 puertos G1/8 | **sin puertos** |
| Placa inyectora (bosquejo) | agujero Ø22,4 pasante | Ø22,4 más **avellanado Ø26,4 × 2,8 mm** para alojar la brida; el fondo queda 0,3 mm bajo la brida, así que la placa no aprieta la punta |

**Consecuencia de montaje:** la brida de Ø26 ya no pasa por el agujero M24 del soporte del banco ni del colector. El orden pasa a ser:

1. Atornillar el cuerpo con su arandela de montaje.
2. Poner la junta de cobre y el remolinador.
3. Poner la arandela de cobre de la punta.
4. Atornillar la punta.

En el motor, la placa se monta al final. Para cambiar el remolinador de calibración igual había que sacar la punta, así que el procedimiento casi no cambia.

## 3. Verificación

- **Modelo propio por vóxeles** ([`verificar_v5.py`](../piezas/elemento_inyector_v5/verificar_v5.py)):
  - Sin interferencias entre el remolinador, el cuerpo, la punta y la junta.
  - El canal entrada → orificio es continuo.
  - Sin las ranuras no hay paso, así que no hay bypass.
- **Fusion** (script [`fusion/inyector_ignis_v5.py`](../piezas/elemento_inyector_v5/fusion/inyector_ignis_v5.py)):
  - Sin interferencias inesperadas en el elemento ni en el motor; solo los solapes de rosca esperados.
  - El corte XZ del motor muestra la brida cubriendo la arandela dentro del avellanado de la placa, y la cámara sin puertos.
- **Distancia del avellanado a los agujeros de GOX de la placa** (calculada, no medida): pared mínima de unos 1,6 mm en la cara de la placa.
- **Guardado** en `GIP > Proyecto_liquido`:
  - "IGNIS Elemento inyector swirl v5"
  - "IGNIS Mini motor v5 (bosquejo)"

## 4. Pendientes

- **Agujeros de GOX de la placa del bosquejo:** el tramo final es de Ø1, por debajo del mínimo de Ø2 acordado para la CNC. Hay que redimensionarlos cuando se trabaje la placa. El elemento cumple la regla.
- Confirmar la conexión real del Allison al tubo del banco y la herramienta mínima del taller.
- Fabricar y medir caudal contra ΔP con los tres remolinadores (0,40, 0,44 y 0,48 mm).
