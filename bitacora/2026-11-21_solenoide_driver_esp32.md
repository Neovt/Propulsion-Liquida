# Bitácora — Proto-tanque: piezas impresas, solenoide y driver

> **Autoría:** Matías Morales (matydrox)
> **Redacción asistida por:** Claude (Opus 5.5 y Sonnet 5.5)
> **Fecha:** 2026-11-21 · **Estado:** borrador

**Proyecto:** Banco de ensayo Propulsión Líquida (IGNIS)
**Período cubierto:** 2026-11-19 a 2026-11-21
**Estado al cierre:** solenoide cableada, probada y funcionando con driver DRV8871 + ESP32 desde el Monitor Serie (`open` / `close`). Sin presión todavía.

---

## 1. Resumen ejecutivo

- Se revisó el CAD del proto-tanque (Fusion) y las 9 boletas de compra de AliExpress (2026-11-08).
- Se diseñaron **2 piezas provisorias impresas** (PETG) para probar a baja presión mientras llegan el adaptador M30 metálico y el tubo sifón.
- Se **cableó la solenoide JT22-02** (conector DIN con LED), se midió la bobina y se validó polaridad.
- Se conectó el **driver DRV8871** a un **ESP32** y se controla la válvula por serie.
- Se resolvieron problemas de **puerto COM** (driver CP210x faltante), **fuente en modo CC** y un **bug de PWM** en el código.

---

## 2. Prototanque (según CAD y plano)

De abajo hacia arriba:

| Elemento | Detalle |
|---|---|
| Tanque/cilindro | Aluminio, cuello roscado M30×1,5 (tipo extintor, sello por o-ring en la cara superior) |
| Adaptador de cuello | M30×1,5 → 1/4" (comprado, **aún no llegó**; provisoriamente impreso, ver §4) |
| Cruz 4 vías | 1/4" **BSPP hembra** (nodo central) |
| Puerto superior | Hacia la solenoide (en el diseño final: pasamuros BSPT + tubo sifón de 6 mm hasta el fondo) |
| Puerto derecho | Transductor de presión G1/4, 0–4 MPa, salida 0,5–4,5 V |
| Puerto izquierdo | Acople rápido neumático 1/4" estilo US (llenado/presurización) |
| Electrónica | ADS1115 (ADC I²C 16 bits) + conversor de nivel lógico I²C 4 canales |

Nota: el CAD mezcla roscas porque en los repositorios no había todas las piezas exactas. **Las boletas son la referencia real de lo comprado.** La cruz es BSPP hembra (lo importante); hay piezas BSPT macho.

---

## 3. Compras (AliExpress, pedidos del 2026-11-08)

| Artículo | Notas |
|---|---|
| Oil Tubing Joint acero al carbono M30×1,5 → 1/4" | **No ha llegado.** Es acero al carbono (el resto es inox/latón) |
| SS304/316L NPT 1/4" macho × hembra | Confirmar uso exacto |
| Conversor de nivel lógico I²C 4 canales | Para ESP32 (3,3 V) con módulos de 5 V |
| ADS1115 (I²C, 16 bits, 4 canales) | Lectura del transductor |
| Adaptadores macho M5/M6/M8/M10/M12 – 1/8", 1/4" BSP (SOREKARA) | Uso pendiente de definir |
| Transductor de presión G1/4, 12 V, 0,5–4,5 V, 0–4 MPa (XIDIBEI) | 40 bar a fondo de escala |
| Cruz 1/8"–1" BSPP hembra (Kongcheng), versión 1/4" | |
| Acople neumático rápido 1/4" rosca externa, US style | Probablemente NPT, verificar |
| Pasamuros 1/4" BSPT, tubo 6 mm, SS304 (China Pneumatic Factory) | **El tubo sifón no ha llegado** |

Solenoide JT22-02 (1/4" BSPP, latón, NC, FKM, 12 V DC) y módulo DRV8871: ya registrados en `Fase1_seleccion_electronica.md`.

### Discrepancia con la Fase 1
La Fase 1 seleccionó un **Veto 4-20 mA (1/2" NPT)** con convertidor SEN0262. Lo comprado es un **transductor 0,5–4,5 V G1/4** leído con **ADS1115**. Es válido, pero el registro de Fase 1 debe actualizarse. Con 40 bar de fondo de escala hay poco margen si se llega a 40 bar finales.

---

## 4. Piezas impresas provisorias (PETG)

Archivos: `P1_adaptador_M30_R14.stl`, `P2_niple_R14_R14.stl`, generador `generar_piezas.py` (numpy; todas las cotas parametrizadas).

| Pieza | Descripción |
|---|---|
| **P1** adaptador cuello | M30×1,5 macho (12 mm de rosca, holgura −0,3 mm) abajo; sello por **o-ring 31×2** en glándula triangular de 45°; hexágono de 40 mm; **R1/4 BSPT macho** (10 mm) arriba; agujero pasante Ø4 mm; ~31 g |
| **P2** niple doble | R1/4 BSPT macho en ambos lados, hexágono de 17 mm, agujero Ø4 mm; une la cruz con la entrada de la solenoide; ~5 g |

Decisiones: roscas cónicas BSPT con **teflón** (uniones temporales, el plástico se deforma); o-ring solo en la rosca M30. Presión máxima absoluta esperada: **8 bar** (pruebas iniciales mucho menos).

Impresión recomendada: PETG, boquilla 0,4, eje vertical (M30 sobre la cama), capa ≤0,12 mm, 100 % de relleno, ≥5 perímetros. Las mallas se verificaron como sólidos cerrados, pero **no se han impreso ni probado a presión**.

Pendiente de medir: Ø exterior de la cara superior del cuello (≥ ~38 mm), profundidad de rosca del cuello (≥12 mm), medida real del o-ring.

Seguridad: primera prueba **hidrostática con agua**; regulador + válvula de alivio; sujetar el peso de la solenoide (queda en voladizo sobre un niple plástico); la válvula tiene flecha de flujo.

---

## 5. Solenoide JT22-02

### Datos medidos
- Placa: **12 V DC, 20 W** (≈1,7 A).
- Resistencia de bobina medida: **≈6,3 Ω** (≈2 A, ≈23 W en frío).
- Conector **DIN 43650** con circuito de LED: **pin 1 → resistencia (~9,75 kΩ) → LED (cátodo) … LED (ánodo) → pin 2**.
- Por tanto: **pin 2 = positivo (+), pin 1 = negativo (−)**. El borne de tierra (PE) **no se conecta**.
- Prueba directa con 12 V: LED verde enciende y se oye el clic. **Cableado y polaridad correctos.**

### Cableado del conector
Cable redondo de 2 hilos, 0,5–0,75 mm², Ø exterior 4,5–7 mm (prensaestopas). Orden de montaje: tuerca → goma → carcasa; hilos en bornes 1 y 2; el bloque de bornes se puede girar en pasos de 90° para elegir la salida del cable.

---

## 6. Driver DRV8871 + ESP32

### Módulo
Chip TI DRV8871. Resistencia **ILIM = "303" = 30 kΩ → límite ≈ 2,1 A** (fórmula 64/R en kΩ, ±10 %). Margen justo para esta bobina (1,7–2 A). Si el clic es débil, cambiar por 20 kΩ ("203", ≈3,2 A).

Pads grandes (potencia): `OUT2, OUT1, VM, GND` (en la cara frontal: `MOTOR 2, 1` y `POWER ⊕ ⊖`). Cabecera de 4 pines: `IN2, IN1, VM, GND`.

### Tabla de conexiones

| Desde | Hacia |
|---|---|
| Fuente **+** | Driver **VM** (⊕) |
| Fuente **−** | Driver **GND** (⊖) |
| Fuente **GND/⏚ (tierra de red)** | No se usa |
| Driver **OUT1** | Hilo **+** de la solenoide (pin 2 del conector) |
| Driver **OUT2** | Hilo **−** de la solenoide (pin 1) |
| Driver **IN1** | ESP32 **D26 (GPIO26)** |
| Driver **IN2** | ESP32 **D27 (GPIO27)** |
| Driver **GND** (cabecera) | ESP32 **GND** |
| Driver **VM** (cabecera) | Sin conectar |
| ESP32 | Alimentado por USB desde el PC |

Reservados para después: **GPIO21/22 (I²C)** para el ADS1115. No usar GPIO34/35 (solo entrada).

### Lógica
Abrir: IN1 alto, IN2 bajo. Cerrar: ambos bajos. Mantención con PWM tras un pulso inicial al 100 %.

### Fuente de poder: MCP M10-SP-303E
- Usar solo **+ y −**; el borne GND es tierra del chasis.
- Perillas: VOLTAGE (voltaje) y CURRENT (límite de corriente). Luces **CV** (normal) y **CC** (limitando).
- Ajuste del límite: apagar salida, unir + y − con un cable, subir CURRENT hasta **2,5 A**, retirar el cable.
- Incidente: tras cambiar los cables por unos más gruesos, la fuente quedó en **CC** (perilla de voltaje sin efecto). Se resolvió revisando el cableado; el módulo **no tiene protección contra polaridad invertida**.

---

## 7. Software y problemas resueltos

### Problema 1 — Puerto COM
- COM4 y COM5 eran **puertos Bluetooth de Windows**, no el ESP32.
- El ESP32 aparecía en el Administrador de dispositivos como **"CP2102 USB to UART Bridge Controller" con triángulo amarillo** (sin driver).
- **Solución:** instalar el driver oficial *CP210x Universal Windows Driver* de Silicon Labs. Luego el puerto COM aparece en "Puertos (COM y LPT)". Placa en Arduino IDE: ESP32 Dev Module / DOIT ESP32 DEVKIT V1 (core Arduino-ESP32 3.x).

### Problema 2 — La válvula se cerraba a ~1 s (v1 del código)
- Causa: la mantención usaba PWM en IN1 con IN2 bajo (decaimiento rápido). La corriente media caía demasiado y el resorte cerraba la válvula.
- **v2:** IN1 alto fijo y PWM en **IN2** (decaimiento lento/freno). Mantención por defecto 70 %. Se añadió el comando `hold NN`.
- Resultado: la válvula se mantiene abierta. El comando `hold` no se confirmó como útil; se puede dejar en 70 %.

### Comandos (Monitor Serie, 115200, "Nueva línea")
`open`, `close`, `status`, `hold 20..100`. Incluye cierre automático de seguridad a los 60 s.

---

## 8. Errores y correcciones durante la sesión

- Se sugirió probar la polaridad del LED con 3 V: **no sirve**, con ~10 kΩ en serie el LED casi no enciende. La prueba válida es con 12 V.
- Se sugirió límite de fuente de 1 A: **demasiado bajo** para esta bobina (~2 A). El límite correcto es 2,5 A.
- La medición inicial de 9,75 kΩ correspondía a la resistencia del LED del conector, no a la bobina.

---

## 9. Pendientes

1. Medir cuello del tanque (Ø exterior, profundidad de rosca) y el o-ring; imprimir P1 y P2.
2. Verificar si el clic del driver es tan firme como con fuente directa (ILIM 30 kΩ); medir corriente real de arranque y de mantención.
3. Ajustar y validar el % de mantención con presión real.
4. Presión mínima de apertura de la válvula (probable asistida por diafragma): probar con aire a 0,5 / 1 / 2 bar.
5. Cablear el ADS1115 (I²C: SDA GPIO21, SCL GPIO22) y el transductor; decidir si se usa el conversor de nivel.
6. Primera prueba **hidrostática con agua** (1,5× la presión de uso, máx. 8 bar), con válvula de alivio.
7. Actualizar `Fase1_seleccion_electronica.md` (transductor y resultados de la bobina).
8. Soporte mecánico para el peso de la solenoide.
9. La válvula (latón + FKM) **no está calificada para GOX**: solo agua, aire, N₂ y queroseno.
10. Esperar el adaptador M30 metálico y el tubo sifón; evaluar el acero al carbono del adaptador frente al resto del montaje.

---

## 10. Archivos asociados

| Archivo | Contenido |
|---|---|
| [`../piezas/generar_piezas.py`](../piezas/generar_piezas.py) | Generador paramétrico (numpy) de P1 y P2; editar los parámetros y volver a correr |
| [`../piezas/P1_adaptador_M30_R14.stl`](../piezas/P1_adaptador_M30_R14.stl) | Adaptador de cuello M30×1,5 → R1/4 BSPT |
| [`../piezas/P2_niple_R14_R14.stl`](../piezas/P2_niple_R14_R14.stl) | Niple doble R1/4 BSPT |
| [`../codigos/solenoide/solenoide.ino`](../codigos/solenoide/solenoide.ino) | Sketch v2 de control por Monitor Serie (durante la sesión se llamó `solenoide_serial.ino`) |

---

## Apéndice — `solenoide.ino` (v2, antes `solenoide_serial.ino`)

```cpp
// Control manual de solenoide JT22-02 (12 V DC, ~2 A) con DRV8871 - ESP32
// Monitor Serie: 115200 baudios, terminación "Nueva línea".
//
// Comandos:  open      -> abre la válvula
//            close     -> cierra la válvula
//            status    -> muestra el estado
//            hold NN   -> cambia el % de mantención (ej: hold 70). 100 = sin PWM
//
// Conexiones:  GPIO26 -> IN1    GPIO27 -> IN2    GND ESP32 -> GND del driver
// Requiere el core Arduino-ESP32 3.x (ledcAttach / ledcWrite por pin).
//
// v2: la mantención usa "slow decay" (IN1 alto fijo, PWM en IN2). Durante el
// apagado del PWM la bobina queda en freno y la corriente casi no cae, así
// el % de mantención sí se traduce en fuerza real. En v1 el PWM iba en IN1
// (fast decay) y la corriente media caía tanto que la válvula se cerraba sola.

const int PIN_IN1 = 26;
const int PIN_IN2 = 27;

const int PWM_FREQ = 20000;      // 20 kHz (silencioso)
const int PWM_BITS = 8;          // duty 0-255
int holdPct        = 70;         // % de mantención tras abrir
const int OPEN_MS  = 300;        // tiempo a 100 % para abrir la válvula
const unsigned long MAX_OPEN_MS = 60000;  // seguridad: cierra sola tras 60 s

bool abierta = false;
unsigned long tAbierta = 0;

void cerrar() {
  ledcWrite(PIN_IN2, 0);           // IN2 bajo
  digitalWrite(PIN_IN1, LOW);      // IN1 bajo -> bobina desenergizada
  abierta = false;
}

void aplicarHold() {
  // IN1 alto fijo; IN2 en PWM. IN2 bajo = conduce, IN2 alto = freno.
  // Fracción conduciendo = holdPct  ->  duty de IN2 = 100 - holdPct
  int duty = 255 * (100 - holdPct) / 100;
  ledcWrite(PIN_IN2, duty);
}

void abrir() {
  digitalWrite(PIN_IN1, HIGH);
  ledcWrite(PIN_IN2, 0);           // 100 % para abrir
  delay(OPEN_MS);
  aplicarHold();
  abierta = true;
  tAbierta = millis();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_IN1, OUTPUT);
  digitalWrite(PIN_IN1, LOW);
  ledcAttach(PIN_IN2, PWM_FREQ, PWM_BITS);
  cerrar();                        // siempre arranca cerrada
  Serial.println("Listo. Comandos: open / close / status / hold NN");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toLowerCase();

    if (cmd == "open") {
      abrir();
      Serial.printf("ABIERTA (mantencion %d %%)\n", holdPct);
    } else if (cmd == "close") {
      cerrar();
      Serial.println("CERRADA");
    } else if (cmd == "status") {
      Serial.printf("Estado: %s, mantencion %d %%\n", abierta ? "ABIERTA" : "CERRADA", holdPct);
    } else if (cmd.startsWith("hold")) {
      int v = cmd.substring(4).toInt();
      if (v >= 20 && v <= 100) {
        holdPct = v;
        if (abierta) aplicarHold();
        Serial.printf("Mantencion = %d %%\n", holdPct);
      } else {
        Serial.println("Usa: hold 20..100");
      }
    } else if (cmd.length() > 0) {
      Serial.println("Comando no valido. Usa: open / close / status / hold NN");
    }
  }

  if (abierta && millis() - tAbierta > MAX_OPEN_MS) {
    cerrar();
    Serial.println("CERRADA (seguridad: 60 s abierta)");
  }
}
```
