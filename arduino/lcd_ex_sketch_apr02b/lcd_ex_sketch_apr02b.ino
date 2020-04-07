#include <Wire.h>
#include "rgb_lcd.h"

rgb_lcd lcd;

int colorR = 0;
int colorG = 0;
int colorB = 0;
int analog_pin = 0;
int button_pin = 2;

void setup() {
  lcd.begin(16, 2);
  lcd.setRGB(colorR, colorG, colorB);
  Serial.begin(9600);
  delay(100);

}

void loop() {
  // put your main code here, to run repeatedly:
  //lcd.setCursor(0, 1);
  //lcd.print(millis()/1000);
  if(Serial.available() > 0) {
    String s = Serial.readString();
    int rotationlength = 0;
    int pos = 0;
    lcd.clear();
    lcd.setRGB(255, 0, 0);
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
  lcd.setRGB(colorR, colorG, colorB);
  delay(100);
  
  if (digitalRead(button_pin) == true) {
    long startpress = millis();
    while (digitalRead(button_pin) == true){}
    long elapsed_time = millis() - startpress;
    if(elapsed_time > 3000) {
      while (true) {
        lcd.clear();
        lcd.print("Default colors: ");
        lcd.setCursor(0, 1);
        //lcd.print(sprintf("%d", analogRead(analog_pin)));
        colorG = analogRead(analog_pin);
        colorG = map(colorG, 0, 1023, 0, 255);
        lcd.print(colorG);
        Serial.println(colorG);
        delay(100);
        if (digitalRead(button_pin) == true) {
          break;
        }
      }
    } else {
      lcd.clear();
    }
  }
  

}
