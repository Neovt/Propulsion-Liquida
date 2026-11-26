// Lectura del transductor de presión XDB401 (0-40 bar, salida 0,5-4,5 V) con ADS1115 - ESP32
// Monitor Serie: 115200 baudios, terminación "Nueva línea".
//
// Salida en CSV:  t_ms,volts,bar
// Comandos:  zero  -> toma la lectura actual como 0 bar (hacer a presión atmosférica)
//            reset -> quita el cero
//
// Conexiones:
//   Sensor  rojo (alimentación) -> +12 V de la fuente
//   Sensor  negro (GND)         -> GND común
//   Sensor  amarillo (señal)    -> ADS1115 A0
//   ADS1115 VDD -> 5 V (VIN del ESP32), GND -> GND común, ADDR -> GND (dirección 0x48)
//   ADS1115 SDA/SCL -> conversor de nivel 4 canales -> ESP32 GPIO21 (SDA) / GPIO22 (SCL)
//   Conversor de nivel: HV = 5 V, LV = 3V3 del ESP32, GND común
//
// Biblioteca: "Adafruit ADS1X15" (Administrador de bibliotecas de Arduino IDE).
// Ganancia 2/3 (±6,144 V): necesaria porque la salida llega a 4,5 V.

#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

const int PIN_SDA = 21;
const int PIN_SCL = 22;

const float V_MIN = 0.5f;     // salida a 0 bar
const float V_MAX = 4.5f;     // salida a fondo de escala
const float P_FS  = 40.0f;    // fondo de escala en bar (0-4 MPa)
const int   N_PROM = 8;       // lecturas promediadas por muestra
const unsigned long PERIODO_MS = 250;

float offsetBar = 0.0f;
unsigned long tUltima = 0;

float leerVoltios() {
  float suma = 0;
  for (int i = 0; i < N_PROM; i++) {
    suma += ads.computeVolts(ads.readADC_SingleEnded(0));
  }
  return suma / N_PROM;
}

float aBar(float v) {
  return (v - V_MIN) / (V_MAX - V_MIN) * P_FS;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(PIN_SDA, PIN_SCL);
  if (!ads.begin(0x48, &Wire)) {
    Serial.println("ERROR: no se encuentra el ADS1115 (revisar SDA/SCL, VDD y direccion 0x48)");
    while (true) delay(1000);
  }
  ads.setGain(GAIN_TWOTHIRDS);                 // +-6,144 V
  ads.setDataRate(RATE_ADS1115_128SPS);
  Serial.println("Listo. Salida: t_ms,volts,bar   (comandos: zero / reset)");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toLowerCase();
    if (cmd == "zero") {
      offsetBar = aBar(leerVoltios());
      Serial.printf("Cero fijado. Offset = %.3f bar\n", offsetBar);
    } else if (cmd == "reset") {
      offsetBar = 0.0f;
      Serial.println("Cero eliminado");
    }
  }

  if (millis() - tUltima >= PERIODO_MS) {
    tUltima = millis();
    float v = leerVoltios();
    float p = aBar(v) - offsetBar;
    Serial.printf("%lu,%.4f,%.3f", millis(), v, p);
    if (v < 0.4f) Serial.print("   <-- FALLA: senal bajo 0,4 V (sensor desconectado o cable cortado)");
    if (v > 4.6f) Serial.print("   <-- FUERA DE RANGO: senal sobre 4,6 V");
    Serial.println();
  }
}
