#include <WiFi.h>
#include "esp_camera.h"

// WiFi ağ bilgileri
const char* ssid = "sez";
const char* password = "11111111";

// Sunucu bilgileri
const char* host = "192.168.159.246";
const uint16_t port = 12345;

void cameraInit(void) {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = CAMD2;
  config.pin_d1 = CAMD3;
  config.pin_d2 = CAMD4;
  config.pin_d3 = CAMD5;
  config.pin_d4 = CAMD6;
  config.pin_d5 = CAMD7;
  config.pin_d6 = CAMD8;
  config.pin_d7 = CAMD9;
  config.pin_xclk = CAMXC;
  config.pin_pclk = CAMPC;
  config.pin_vsync = CAMV;
  config.pin_href = CAMH;
  config.pin_sscb_sda = CAMSD;
  config.pin_sscb_scl = CAMSC;
  config.pin_pwdn = -1;
  config.pin_reset = -1;
  config.xclk_freq_hz = 15000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_UXGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_UXGA;
    config.fb_count = 2;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Kamera başlatma hatası! Hata kodu: 0x%x", err);
    return;
  }

  sensor_t* s = esp_camera_sensor_get();
  s->set_framesize(s, FRAMESIZE_UXGA);
}

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi bağlantısı kuruldu.");

    cameraInit();
    Serial.println("Kamera hazır, fotoğraflar gönderilecek.");
}

void captureAndSendImage() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Kamera fotoğraf alamadı!");
        return;
    }

    WiFiClient tempClient;
    if (tempClient.connect(host, port)) {
        tempClient.write(fb->buf, fb->len);
        Serial.println("Fotoğraf gönderildi.");
    } else {
        Serial.println("Sunucuya bağlanılamadı.");
    }

    tempClient.stop();
    esp_camera_fb_return(fb);
}

void loop() {
    delay(1001); // 5 Saniye Bekler
    captureAndSendImage(); // Fotoğraf çek ve gönder
}
