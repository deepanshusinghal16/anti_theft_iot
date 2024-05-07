#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char *WIFI_SSID = "Singhal-2.4Ghz";
const char *WIFI_PASS = "9599521464";

WebServer server(80);
bool emergencyAlert = false;

static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

void serveJpg()
{
    auto frame = esp32cam::capture();
    if (frame == nullptr)
    {
        Serial.println("CAPTURE FAIL");
        server.send(503, "", "");
        return;
    }
    // Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
    // static_cast<int>(frame->size()));

    server.setContentLength(frame->size());
    server.send(200, "image/jpeg");
    WiFiClient client = server.client();
    frame->writeTo(client);
}

void handleJpgLo()
{
    if (!esp32cam::Camera.changeResolution(loRes))
    {
        Serial.println("SET-LO-RES FAIL");
    }
    serveJpg();
}

void handleJpgHi()
{
    if (!esp32cam::Camera.changeResolution(hiRes))
    {
        Serial.println("SET-HI-RES FAIL");
    }
    serveJpg();
}

void handleJpgMid()
{
    if (!esp32cam::Camera.changeResolution(midRes))
    {
        Serial.println("SET-MID-RES FAIL");
    }
    serveJpg();
}

void handleRoot()
{
    String html;
    if (emergencyAlert)
    {
        html = "<!DOCTYPE html>\
<html>\
<head>\
  <title>ESP32 Camera Stream - EMERGENCY</title>\
  <style>\
    /* Your CSS styling here */\
    .emergency { color: red; font-size: 20px; }\
  </style>\
</head>\
<body>\
  <h1 class='emergency'>EMERGENCY: Please take necessary action!</h1>\
  <img src='/cam-mid.jpg' alt='Camera Feed'>\
  <script>\
    // Your JavaScript code here\
  </script>\
</body>\
</html>";
    }
    else
    {
        html = "<!DOCTYPE html>\
<html>\
<head>\
  <title>ESP32 Camera Stream</title>\
  <style>\
    /* Your CSS styling here */\
  </style>\
</head>\
<body>\
  <h1>ESP32 Camera Stream</h1>\
  <img src='/cam-mid.jpg' alt='Camera Feed'>\
  <script>\
    // Your JavaScript code here\
  </script>\
</body>\
</html>";
    }
    server.send(200, "text/html", html);
}

void handleEmergencyAlert()
{
    emergencyAlert = true;
    Serial.println("Emergency alert received!");
    server.send(200, "text/plain", "Emergency"); // Send a response to the client
}

void setup()
{
    Serial.begin(115200);
    Serial.println("Hello ..!");

    {
        using namespace esp32cam;
        Config cfg;
        cfg.setPins(pins::AiThinker);
        cfg.setResolution(midRes);
        cfg.setBufferCount(2);
        cfg.setJpeg(80);

        bool ok = Camera.begin(cfg);
        Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
    }

    WiFi.persistent(false);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.println("Trying to Connect to Wifi..!");
    }

    Serial.print("http://");
    Serial.println(WiFi.localIP());

    server.on("/", handleRoot);
    server.on("/cam-lo.jpg", handleJpgLo);
    server.on("/cam-hi.jpg", handleJpgHi);
    server.on("/cam-mid.jpg", handleJpgMid);
    server.on("/emergency", handleEmergencyAlert); // New route handler for emergency alert

    server.begin();
}

void loop()
{
    server.handleClient();
    // if  (emergencyAlert) {
    //   // Take appropriate action for emergency situation
    //   // For example, trigger an alarm, send notification, etc.
    //   // Reset emergency flag after handling the alert
    //   emergencyAlert = false;
    // }
}
