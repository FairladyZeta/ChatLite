#include <Wire.h>
#include "rgb_lcd.h"

rgb_lcd lcd;
int colorR = 100;
int colorG = 100;
int colorB = 100;

void setup() {
  lcd.begin(16, 2);
  lcd.setRGB(colorR, colorG, colorB);
  Serial.begin(9600);
  delay(1000);
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
    lcd.setRGB(colorR, colorG, colorB);
  }

  delay(100);

}
