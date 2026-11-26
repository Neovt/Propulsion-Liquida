# Elemento inyector v4 (15 g/s, entrada macho) y fe de erratas del 26-11

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5)
> **Fecha:** 2026-11-26 · **Estado:** borrador

## 1. Fe de erratas de [la entrada anterior](2026-11-26_inyector_elemento_y_mini_motor.md)

- **Caudal del Allison 250.** Se escribió "27,8 g/s a 5 bar" a partir del caso de Fluent encontrado en los archivos. La memoria de A. Espinoza (Fig. 51, ensayo real con queroseno) da en cambio:

| Presión | Caudal |
|---|---|
| 10 bar | ≈ 7,5 g/s |
| 14 bar | ≈ 14 g/s |
| 18 bar | ≈ 20 g/s |
| 30 bar | ≈ 35,6 g/s |

  Cono de 76–82° (Fig. 50). El caso de Fluent no corresponde a la curva experimental, probablemente por condiciones de borde distintas. **Vale el dato experimental.**
- **Elemento v3:** dos defectos señalados por Matías al revisarlo:
  - **Entrada hembra.** Debía ser macho, como la del Allison.
  - **Sin un sello definido** entre la punta y el cuerpo. Había una ranura abierta de 0,5 mm por donde se fugaría el combustible que pasara por la rosca.
- **Mini motor v3:** las juntas de grafito (1,5 mm) quedaban más altas que su ranura (1,0 mm). En el modelo se veía una abertura sobre la placa: la "junta abierta" del corte.

## 2. Requisitos del v4 (definidos por Matías)

- Unos **15 g/s de queroseno con el tanque a 8 bar**, garantizados por geometría.
- **Sobredimensionado**, fácil de mecanizar y **sin herramientas finas**. Se mantiene el criterio de no usar nada menor que Ø2.
- **Forma exterior parecida al Allison**, para usar sus mismas instalaciones (tubo de acero de 6 mm del banco).
- Por ahora no se busca empuje: se busca **caracterizar** el sistema.

## 3. Lo que dice la memoria sobre el banco

- Tubería **rígida de acero de 6 mm** (Fig. 40) y racores de compresión de doble férula (válvula de aguja, Fig. 39).
- Válvula de bola de 1/4" (Fig. 38), manómetro de 0–40 bar y rotámetro de 1–4 L/min.
- Inyector montado vertical, apuntando hacia abajo, dentro de una caja de acrílico (Fig. 44).
- **No se especifica** la conexión física entre el tubo y la entrada macho del Allison.

## 4. Diseño v4

Archivos en [`../piezas/elemento_inyector_v4/`](../piezas/elemento_inyector_v4/).

| Elemento | Detalle |
|---|---|
| Entrada | **macho M12×1,5 con cono interior de 24° (DIN 2353 / ISO 8434-1, serie L6)**. El tubo de 6 mm del banco se conecta directo con tuerca y anillo cortante comerciales. Paso interior Ø4 (Allison: Ø4,1). **Supuesto:** si el Allison usa otra norma, solo cambia esta espiga |
| Cuerpo | hexágono 30 con agujero de alambre de seguridad; hombro de sello con arandela de cobre 24×30×2; montaje M24×1,5; frente liso Ø22 |
| Sellos | **junta de cobre** Ø13,6/Ø15,9 × 0,5 bajo el remolinador (como la pieza 9 del Allison) y **arandela de cobre** Ø18,5/Ø22 × 1 entre la brida de la punta y el cuerpo. **No hay ranuras abiertas**: la punta aprieta el remolinador sobre su junta y la brida sella contra el cuerpo |
| Remolinador | Ø16 × 6, **2 agujeros axiales Ø2** y **2 ranuras tangenciales 2,0 × 0,44** (fresa Ø2) |
| Punta | M18×1,5; brida Ø22 con planos de llave 19 y alambre de seguridad; cámara de remolino Ø8 × 4, cono de 90°, **orificio Ø2 × 1,5** |
| Largo | 55 mm desde la punta de la espiga hasta la salida |

**Por qué 2 ranuras de solo 0,44 mm.** Con un orificio de Ø2 (mínimo de taller), un swirl normal pasaría más de 30 g/s a 7,5 bar. Para llegar a 15 g/s sin herramienta fina, el giro se hace más fuerte (constante geométrica A ≈ 5,35). El costo es un cono más abierto, de unos 109°, en vez de los ~80° del Allison.

**Calibración** (estimación por teoría de Abramovich; el caudal real se mide en el banco): se fabrican **tres remolinadores** y se elige el que dé el caudal medido más cercano a 15 g/s.

| Profundidad de ranura | Queroseno a 5 / 7,5 / 8 / 10 bar | Cono |
|---|---|---|
| 0,40 mm | 11,4 / 14,0 / 14,4 / 16,1 g/s | 111° |
| **0,44 mm** | 12,3 / **15,1** / 15,6 / 17,4 g/s | 109° |
| 0,48 mm | 13,2 / 16,2 / 16,7 / 18,7 g/s | 107° |

Con 2 L de queroseno a 15 g/s, la descarga dura unos **107 s**. Al aire libre el elemento no tiene límite térmico, porque el combustible lo enfría; más duración solo requiere más combustible.

## 5. Verificado en el modelo independiente

([`verificar_v4.py`](../piezas/elemento_inyector_v4/verificar_v4.py), vóxeles de 0,08–0,1 mm)

- Sin interferencias entre el remolinador, el cuerpo, la punta y la junta.
- El canal entrada → orificio es continuo, y **sin las ranuras el canal queda cortado**: todo el caudal pasa por ellas y gira.
- Paredes mínimas: cuerpo 2,2 mm, remolinador 1,5 mm, punta 2,6 mm.
- El borde interior de los agujeros axiales queda a 0,5 mm de la cámara de remolino, así que no hay bypass sin giro.

## 6. Estado en Fusion

- El script [`fusion/inyector_ignis_v4.py`](../piezas/elemento_inyector_v4/fusion/inyector_ignis_v4.py) quedó copiado en el PC (`Descargas\fusion_inyector_cnc\inyector_ignis_v4`). **No alcanzó a ejecutarse**: Fusion se cerró durante la sesión.
- El script también regenera el bosquejo del motor con las juntas de grafito a ras, de 1,0 mm en ranura de 1,0 mm.
- En el estado de tareas de Fusion queda una **carga pausada de `Allison250_part1bodies`**, de un primer intento. Si se reanuda, el archivo aparecería en la raíz de GIP y habría que moverlo a `Proyecto_liquido` o cancelarlo.

## 7. Pendientes

1. Ejecutar el script v4 en Fusion, revisar el corte y guardar en `GIP > Proyecto_liquido`.
2. Confirmar la conexión real del Allison al tubo del banco (DIN 24° o abocinado 37°) y medir su rosca de montaje. Ajustar la espiga y el M24 si hace falta.
3. Confirmar con el taller que Ø2 es la herramienta mínima.
4. Fabricar en latón el cuerpo, la punta y los tres remolinadores; medir caudal contra ΔP y el ángulo del cono en el banco.
