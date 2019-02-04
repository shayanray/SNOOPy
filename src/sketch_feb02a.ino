#include <Servo.h>

Servo hor;

int pos=0;
int disp;

void setup() {
  Serial.begin(9600);
  hor.attach(5);
  pos = 90;
  hor.write(pos);
  delay(10);
  disp = 0;
}

/*void(* resetFunc) (void) = 0; //declare reset function @ address 0*/



void loop() {

  /*delay(100); */

  while(Serial.available()>0){
    
    disp = Serial.read();
    if(disp == 90 && pos != 90){
      /*resetFunc();  */
      pos = 90;
      hor.write(pos);
      delay(300);
    }

    else if(disp > 100 ){ /* && pos < 180 */
      pos+=20;
      hor.write(pos);
      delay(3);
    }
    else if(disp < 100 ){ /* && pos > 0 */
      pos-=20;
      hor.write(pos);
      delay(3);
    }
    /*
    else if(disp >= 100){
      
      
      for (pos = 90; pos <= 180; pos += 1) { // goes from 90 degrees to 180 degrees
          // in steps of 20 degree
          hor.write(pos);              // tell servo to go to position in variable 'pos'
          delay(1);                       // waits 15ms for the servo to reach the position
      }
      
    }
    
    else if(disp < 100){

      
      for (pos = 90; pos >= 0; pos -= 1) { // goes from 90 degrees to 0 degrees
        hor.write(pos);              // tell servo to go to position in variable 'pos'
        delay(1);                       // waits 15ms for the servo to reach the position
      }
      
    }*/

    
  }

}
