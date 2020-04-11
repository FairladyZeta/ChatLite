#include <Wire.h>
#include "rgb_lcd.h"

rgb_lcd lcd;

//int colorR = 0, colorG = 0, colorB = 0;
int dcolors[3] = {0, 0, 0};
int ucolors[3] = {255, 0, 0};
char ccolors[3] = {'R', 'G', 'B'};
int analog_pin = 0, button_pin = 2;

void setup() {
  lcd.begin(16, 2);
  lcd.setRGB(dcolors[0], dcolors[1], dcolors[2]);
  Serial.begin(9600);
  delay(100);

}


void loop() {
  if(Serial.available() > 0) {
    String s = Serial.readString();
    /*
    if(s.substring(0, s.length() - 1)=="889574AEBACDA6BFD3E534E2B49B8028"){
      Serial.read
    }*/
    int rotationlength = 0;
    int pos = 0;
    lcd.clear();
    lcd.setRGB(ucolors[0], ucolors[1], ucolors[2]);
    if(s.length() > 16 && s.length() < 32) {
      lcd.print(s.substring(0, 16));
      lcd.setCursor(0, 1);
      lcd.print(s.substring(16));
    } else if(s.length() > 32) {
      int chunks = s.length() / 16;
      //Serial.write("s");
      for (int i = 0; i < chunks; i++) {
        int pos = i * 16;
        int pos2 = (i + 1) * 16;
        int pos3 = (i + 2) * 16;
        lcd.clear();
        lcd.print(s.substring(pos, pos2));
        lcd.setCursor(0, 1);
        lcd.print(s.substring(pos2, pos3));
        delay(800);
      }
    } else {
      lcd.print(s);
    }
    delay(1000);
  }
  lcd.setRGB(dcolors[0], dcolors[1], dcolors[2]);
  delay(100);
  if (digitalRead(button_pin) == true) {
    long startpress = millis();
    while (digitalRead(button_pin) == true){}
    long elapsed_time = millis() - startpress;
    if(elapsed_time > 3000) {
      lcd.clear();
      Serial.println("eep");
    } else {
      for (int i; i < 3; i++) {
        delay(200);
        while (digitalRead(button_pin) == false) {
          lcd.clear();
          lcd.setRGB(dcolors[0], dcolors[1], dcolors[2]);
          lcd.print("# colors RGB: ");
          dcolors[i] = analogRead(analog_pin);
          dcolors[i] = map(dcolors[i], 0, 1023, 0, 255);
          lcd.setCursor(0, 1);
          //lcd.print(ccolors[i]);
          lcd.print(dcolors[i]);
          delay(100);
          Serial.println(dcolors[i]);
        }
        lcd.clear();
      }
      delay(200);
      for (int i; i < 3; i++) {
        delay(200);
        while (digitalRead(button_pin) == false) {
          lcd.clear();
          lcd.setRGB(ucolors[0], ucolors[1], ucolors[2]);
          lcd.print("! colors RGB: ");
          ucolors[i] = analogRead(analog_pin);
          ucolors[i] = map(ucolors[i], 0, 1023, 0, 255);
          lcd.setCursor(0, 1);
          //lcd.print(ccolors[i]);
          lcd.print(ucolors[i]);
          delay(100);
          Serial.println(ucolors[i]);
        }
        lcd.clear();
      }

      lcd.clear();
      //setcolor(ucolors, ccolors, "Ntfcn Color");
      delay(100);
      elapsed_time = 0;
      //lcd.print(sprintf("%d", analogRead(analog_pin)));
      //input = analogRead(analog_pin);
      //colorG = map(colorG, 0, 1023, 0, 255);
     
    }
  }
}
