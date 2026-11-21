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
