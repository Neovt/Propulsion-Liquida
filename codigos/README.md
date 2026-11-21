# Códigos — IGNIS

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Sonnet 5.5)
> **Fecha:** 2026-11-21 · **Estado:** borrador

Aquí vive todo el código del proyecto (control, adquisición de datos, pruebas). Cada componente tiene su propia carpeta, y dentro de ella el programa lleva el mismo nombre que la carpeta. Esa regla es la que exige Arduino IDE para abrir un sketch.

```
codigos/
  solenoide/solenoide.ino
  presion/presion.ino          ← futuro: lectura del transductor
```

## Contenido

| Carpeta | Qué hace | Hardware | Estado |
|---|---|---|---|
| [`solenoide/`](solenoide/solenoide.ino) | Abre y cierra la solenoide JT22-02 por el Monitor Serie (`open`, `close`, `status`, `hold NN`) | ESP32 DevKit + driver DRV8871 | probado sin presión |

## Cómo usarlos

- Abrir el `.ino` con Arduino IDE (placa **ESP32 Dev Module**, core Arduino-ESP32 3.x).
- El cableado y las pruebas de cada programa están en las entradas de [`../bitacora/`](../bitacora/README.md).
- Cada programa debe llevar en su cabecera las conexiones y los comandos, y un comentario si cambia el comportamiento respecto a la versión anterior.
