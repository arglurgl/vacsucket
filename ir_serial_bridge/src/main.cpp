#include <Arduino.h>
#include <IRremote.hpp>
#include <math.h>

// infrared
//#define IR_RECEIVE_PIN 2
#define DISABLE_CODE_FOR_RECEIVER // Disables static receiver code like receive timer ISR handler and static IRReceiver and irparams data. Saves 450 bytes program memory and 269 bytes RAM if receiving functions are not required.
#define EXCLUDE_EXOTIC_PROTOCOLS  // Saves around 240 bytes program memory if IrSender.write is used
//#define SEND_PWM_BY_TIMER         // Disable carrier PWM generation in software and use (restricted) hardware PWM.
//#define USE_NO_SEND_PWM           // Use no carrier PWM, just simulate an active low receiver signal. Overrides SEND_PWM_BY_TIMER definition
#define IR_SEND_PIN 10
#define COMMAND_DELAY 10 //us
#define COMMAND_REPEATS 2

void onoff(){  
  IrSender.sendNEC(0xF700, 0xE, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void forward(){
  IrSender.sendNEC(0xF700, 0x1, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void back(){
  IrSender.sendNEC(0xF700, 0x5, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void left(){
  IrSender.sendNEC(0xF700, 0x0, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void right(){
  IrSender.sendNEC(0xF700, 0x2, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void startstop(){
  IrSender.sendNEC(0xF700, 0x6, COMMAND_REPEATS); 
  delay(COMMAND_DELAY);
}

void setup()
{
  IrSender.begin(IR_SEND_PIN); // Start with IR_SEND_PIN 

  onoff(); //switch robot off standby
  
  Serial.begin(9600);
  Serial.println("Setup done.");
}
 
void loop()
{
  if (Serial.available()){
    char command;
    Serial.readBytes(&command, 1);
    switch (command) {
      case 'o':
        Serial.println("Sending on/off");
        onoff();
        break;      
      case 'f':
        Serial.println("Sending forward");
        forward();
        break;
      case 'b':
        Serial.println("Sending back");
        back();
        break;
      case 'l':
        Serial.println("Sending left");
        left();
        break;
      case 'r':
        Serial.println("Sending right");
        right();
        break;
      case 's':
        Serial.println("Sending start/stop");
        startstop();
        break;

      default:
        Serial.println("Unknown command character received");
    }
    
    // flush all chars which arrived during execution time,
    // we are only interested in the newest state on the next loop
    int chars_to_ignore = Serial.available();
    while(chars_to_ignore > 0){
      Serial.read();
      chars_to_ignore --;
    }
  }
}
