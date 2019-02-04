#include <Servo.h>

Servo hor;

int curr;
int disp;

void setup() {
  Serial.begin(9600);
  hor.attach(5);
  curr = 90;
  hor.write(curr);
  delay(10);
  disp = 0;
}

void loop() {
  while(Serial.available()>0){
    
    disp = Serial.read();
    if(disp>150&&curr!=180){
      curr+=45;
      hor.write(curr);
      delay(10);
    } else { /* if(disp<-150&&curr!=0) */
      curr-=45;
      hor.write(curr);
      delay(10);
    }
  }

/*while(Serial.available()>0){
  disp = Serial.read();
  if(disp!=1){
  curr+=1;
  hor.write(curr);
  delay(10);
}
}*/

}