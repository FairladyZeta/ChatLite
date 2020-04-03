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
    lcd.clear();
    lcd.setRGB(255, 0, 0);
    lcd.print(s);
    delay(1000);
    lcd.setRGB(colorR, colorG, colorB);
  }

  delay(100);

}
