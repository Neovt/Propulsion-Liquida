// Banco de ensayo IGNIS - ESP32: lectura de presión + control de la solenoide, con seguridad local.
// Reemplaza a presion.ino y solenoide.ino (se pueden seguir usando por separado para pruebas sueltas).
//
// Se usa con la interfaz codigos/interfaz/banco.html (Chrome, Web Serial), o a mano desde el
// Monitor Serie (115200 baudios, "Nueva línea").
//
// Conexiones (las mismas de las pruebas del 21-11 y 26-11):
//   Transmisor XDB401 (0-40 bar, 0,5-4,5 V): rojo +12 V, negro GND común, amarillo -> ADS1115 A1
//   ADS1115: VDD 5 V (VIN del ESP32), GND común, ADDR a GND (0x48), SDA/SCL por el conversor de nivel
//            -> ESP32 GPIO21 (SDA) / GPIO22 (SCL)
//   DRV8871: IN1 -> GPIO26, IN2 -> GPIO27, GND -> GND del ESP32; OUT1/OUT2 a la solenoide JT22-02 (NC)
//
// Salida (una línea por mensaje):
//   D,t_ms,volts,bar,valvula(0/1),flags        datos, 20 por segundo
//       flags: 0 normal | 1 sobre alarma | 2 purgando | 4 falla de sensor (bajo 0,4 V o sobre 4,6 V)
//   E,t_ms,texto                               eventos (apertura, cierre, motivo, alarmas)
//   S,alarma_bar,purga_bar,max_abierta_s,offset_bar   configuración actual
//
// Comandos:
//   OPEN            abre (100 % durante 300 ms y luego mantención al 70 %)
//   CLOSE           cierra
//   PULSE s         abre durante s segundos (0,1 a 600) y cierra sola
//   ZERO            toma la lectura actual como 0 bar (hacer con el tanque abierto) y la guarda
//   UNZERO          borra el cero
//   ALARM b         límite de alarma en bar (solo avisa)
//   PURGE b         presión de purga en bar: sobre ella la válvula se abre sola para descargar
//                   (máximo 8 bar, por las piezas impresas); se cierra al bajar de purga - 0,3 bar
//   MAXOPEN s       tiempo máximo abierta en apertura manual (5 a 600 s); luego se cierra sola
//   HB              latido de la interfaz. Tras el primer HB, si pasan 2 s sin comandos la
//                   válvula se cierra (pérdida de comunicación -> estado seguro)
//   STATUS          reenvía la configuración
//
// Seguridad:
//   - Al arrancar, al reiniciarse o al perder la comunicación con la interfaz, la válvula se cierra.
//   - Si se corta la energía, la solenoide (NC) se cierra sola.
//   - La purga NO reemplaza al regulador ni a la válvula de alivio: depende de que la línea de
//     descarga esté libre y de que el transmisor funcione.

#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>

// ---------- Pines y constantes ----------
const int PIN_SDA = 21, PIN_SCL = 22;
const int PIN_IN1 = 26, PIN_IN2 = 27;
const uint8_t CANAL = 1;                 // el cable amarillo está soldado en A1

const float V_MIN = 0.5f, V_MAX = 4.5f, P_FS = 40.0f;
const unsigned long PERIODO_MS = 50;     // 20 datos por segundo
const int N_PROM = 4;                    // lecturas promediadas por dato (ADS a 250 SPS)

const int PWM_FREQ = 20000, PWM_BITS = 8;
const int HOLD_PCT = 70;                 // mantención tras abrir (v2 de solenoide.ino)
const int OPEN_MS = 300;                 // tiempo al 100 % para abrir

const unsigned long WATCHDOG_MS = 2000;
const float PURGA_MAX = 8.0f;            // tope de la presión de purga
const float HIST_PURGA = 0.3f;

// ---------- Estado ----------
Adafruit_ADS1115 ads;
Preferences prefs;

float offsetBar = 0.0f;
float alarmaBar = 3.0f;
float purgaBar = 4.0f;
unsigned long maxAbiertaMs = 60000;

bool abierta = false;
bool purgando = false;
bool enPulso = false;
unsigned long tApertura = 0, duracionPulso = 0;
bool alarmaActiva = false;

bool latidoActivo = false;
unsigned long tUltimoComando = 0;
unsigned long tUltimoDato = 0;

float ultimaP = 0.0f, ultimaV = 0.0f;
bool fallaSensor = false;

// ---------- Válvula ----------
void evento(const String &txt) {
  Serial.printf("E,%lu,%s\n", millis(), txt.c_str());
}

void cerrar(const char *motivo) {
  ledcWrite(PIN_IN2, 0);
  digitalWrite(PIN_IN1, LOW);
  if (abierta) evento(String("CERRADA ") + motivo);
  abierta = false;
  enPulso = false;
  purgando = false;
}

void abrir(const char *motivo) {
  if (!abierta) {
    digitalWrite(PIN_IN1, HIGH);
    ledcWrite(PIN_IN2, 0);               // 100 % para vencer el resorte
    delay(OPEN_MS);
    ledcWrite(PIN_IN2, 255 * (100 - HOLD_PCT) / 100);   // slow decay: IN1 alto, PWM en IN2
    abierta = true;
    tApertura = millis();
    evento(String("ABIERTA ") + motivo);
  }
}

// ---------- Lectura ----------
float leerVoltios() {
  float s = 0;
  for (int i = 0; i < N_PROM; i++) s += ads.computeVolts(ads.readADC_SingleEnded(CANAL));
  return s / N_PROM;
}

float aBar(float v) { return (v - V_MIN) / (V_MAX - V_MIN) * P_FS; }

void enviarConfig() {
  Serial.printf("S,%.2f,%.2f,%lu,%.3f\n", alarmaBar, purgaBar, maxAbiertaMs / 1000, offsetBar);
}

// ---------- Comandos ----------
void procesar(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;
  tUltimoComando = millis();

  int esp = cmd.indexOf(' ');
  String op = esp < 0 ? cmd : cmd.substring(0, esp);
  float arg = esp < 0 ? NAN : cmd.substring(esp + 1).toFloat();

  if (op == "HB") {
    if (!latidoActivo) { latidoActivo = true; evento("INTERFAZ CONECTADA"); enviarConfig(); }
  } else if (op == "OPEN") {
    enPulso = false;
    abrir("(manual)");
  } else if (op == "CLOSE") {
    cerrar("(manual)");
  } else if (op == "PULSE") {
    if (isnan(arg) || arg < 0.1f || arg > 600.0f) { evento("PULSE fuera de rango (0,1 a 600 s)"); return; }
    cerrar("(nuevo pulso)");
    duracionPulso = (unsigned long)(arg * 1000.0f);
    abrir((String("(pulso ") + String(arg, 1) + " s)").c_str());
    enPulso = true;
  } else if (op == "ZERO") {
    offsetBar = aBar(leerVoltios());
    prefs.putFloat("offset", offsetBar);
    evento(String("CERO fijado, offset ") + String(offsetBar, 3) + " bar");
    enviarConfig();
  } else if (op == "UNZERO") {
    offsetBar = 0.0f;
    prefs.putFloat("offset", offsetBar);
    evento("CERO borrado");
    enviarConfig();
  } else if (op == "ALARM") {
    if (isnan(arg) || arg <= 0 || arg > P_FS) { evento("ALARM fuera de rango"); return; }
    alarmaBar = arg; prefs.putFloat("alarma", alarmaBar);
    evento(String("ALARMA ") + String(alarmaBar, 2) + " bar");
    enviarConfig();
  } else if (op == "PURGE") {
    if (isnan(arg) || arg <= 0 || arg > PURGA_MAX) { evento("PURGE fuera de rango (0 a 8 bar)"); return; }
    purgaBar = arg; prefs.putFloat("purga", purgaBar);
    evento(String("PURGA ") + String(purgaBar, 2) + " bar");
    enviarConfig();
  } else if (op == "MAXOPEN") {
    if (isnan(arg) || arg < 5 || arg > 600) { evento("MAXOPEN fuera de rango (5 a 600 s)"); return; }
    maxAbiertaMs = (unsigned long)(arg * 1000.0f); prefs.putULong("maxab", maxAbiertaMs);
    evento(String("MAX ABIERTA ") + String((int)arg) + " s");
    enviarConfig();
  } else if (op == "STATUS") {
    enviarConfig();
  } else {
    evento("COMANDO DESCONOCIDO: " + cmd);
  }
}

// ---------- Programa ----------
void setup() {
  pinMode(PIN_IN1, OUTPUT);
  digitalWrite(PIN_IN1, LOW);
  ledcAttach(PIN_IN2, PWM_FREQ, PWM_BITS);
  ledcWrite(PIN_IN2, 0);                 // válvula cerrada desde el primer instante

  Serial.begin(115200);
  Serial.setTimeout(20);                 // no bloquear el lazo esperando un fin de línea
  Wire.begin(PIN_SDA, PIN_SCL);

  prefs.begin("banco", false);
  offsetBar   = prefs.getFloat("offset", 0.0f);
  alarmaBar   = prefs.getFloat("alarma", 3.0f);
  purgaBar    = prefs.getFloat("purga", 4.0f);
  maxAbiertaMs = prefs.getULong("maxab", 60000);

  if (!ads.begin(0x48, &Wire)) {
    while (true) { Serial.println("E,0,ERROR: no responde el ADS1115 (SDA/SCL, VDD, 0x48)"); delay(1000); }
  }
  ads.setGain(GAIN_TWOTHIRDS);           // +-6,144 V
  ads.setDataRate(RATE_ADS1115_250SPS);

  evento("LISTO banco v1");
  enviarConfig();
}

void loop() {
  // Comandos
  while (Serial.available()) procesar(Serial.readStringUntil('\n'));

  unsigned long ahora = millis();

  // Pérdida de comunicación con la interfaz -> estado seguro
  if (latidoActivo && ahora - tUltimoComando > WATCHDOG_MS) {
    latidoActivo = false;
    if (!purgando) cerrar("(sin comunicacion)");
    evento("INTERFAZ PERDIDA");
  }

  // Fin de pulso y tiempo máximo abierta
  if (abierta && enPulso && ahora - tApertura >= duracionPulso) cerrar("(fin de pulso)");
  if (abierta && !enPulso && !purgando && ahora - tApertura >= maxAbiertaMs) cerrar("(tiempo maximo)");

  // Dato
  if (ahora - tUltimoDato >= PERIODO_MS) {
    tUltimoDato = ahora;
    ultimaV = leerVoltios();
    ultimaP = aBar(ultimaV) - offsetBar;
    fallaSensor = (ultimaV < 0.4f || ultimaV > 4.6f);

    // Alarma (solo aviso)
    bool sobre = !fallaSensor && ultimaP > alarmaBar;
    if (sobre && !alarmaActiva) evento(String("ALARMA presion ") + String(ultimaP, 2) + " bar");
    alarmaActiva = sobre;

    // Purga automática por sobrepresión
    if (!fallaSensor && ultimaP > purgaBar && !purgando) {
      enPulso = false;
      abrir("(PURGA por sobrepresion)");
      purgando = true;
    } else if (purgando && (fallaSensor || ultimaP < purgaBar - HIST_PURGA)) {
      purgando = false;
      cerrar(fallaSensor ? "(fin de purga: falla de sensor)" : "(fin de purga)");
    }

    int flags = (alarmaActiva ? 1 : 0) | (purgando ? 2 : 0) | (fallaSensor ? 4 : 0);
    Serial.printf("D,%lu,%.4f,%.3f,%d,%d\n", ahora, ultimaV, ultimaP, abierta ? 1 : 0, flags);
  }
}
