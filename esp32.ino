#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// عدّل هذه القيم قبل التشغيل
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.10:5000/api/sensors";

const int PH_PIN = 34;
const int TDS_PIN = 35;
const int TURBIDITY_PIN = 32;
const int ONE_WIRE_BUS = 4;

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

float readVoltage(int pin) {
  return analogRead(pin) * (3.3f / 4095.0f);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  tempSensor.begin();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWi-Fi connected");
}

void loop() {
  tempSensor.requestTemperatures();
  float temperature = tempSensor.getTempCByIndex(0);
  // هذه تحويلات أولية/تجريبية فقط؛ عايرها حسب لوحة الحساس ومواصفاته.
  float phRaw = readVoltage(PH_PIN);
  float tdsRaw = readVoltage(TDS_PIN);
  float turbidityRaw = readVoltage(TURBIDITY_PIN);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    String body = "{\"ph\":" + String(phRaw, 3) +
                  ",\"tds\":" + String(tdsRaw, 3) +
                  ",\"turbidity\":" + String(turbidityRaw, 3) +
                  ",\"temperature\":" + String(temperature, 2) + "}";
    int code = http.POST(body);
    Serial.printf("HTTP response: %d\n", code);
    Serial.println(http.getString());
    http.end();
  }
  delay(5000);
}
