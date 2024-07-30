#include <CommandHandler.h>
#include <Stepper.h>
CommandHandler SerialCommandHandler(" ", ';');

// stepper init
const int stepsPerRevolution = 2038;
int currentPosition_1 = 0;
int openPosition_1 = 0;
int closedPosition_1 = 0;

int currentPosition_2 = 0;
int openPosition_2 = 0;
int closedPosition_2 = 0;

bool isHomed_1 = false;
bool isHomed_2 = false;

Stepper iris = Stepper(stepsPerRevolution, 8, 10, 9, 11);
const int closedpin = 6;
const int openedpin = 5;
const int closedpin2 = 4;
const int openedpin2 = 3;
const int stepamount = 25;
const int en_1 = 12;
const int en_2 = 13;

void setup() {
    // Initialize serial communication
    Serial.begin(115200);
    SerialCommandHandler.setCmdHeader("FEEDBACK");
    SerialCommandHandler.setDefaultHandler(unrecognized);
    SerialCommandHandler.addCommand("LED", HandleLEDCommand);
    SerialCommandHandler.addCommand("CLOSE", closeIris);
    SerialCommandHandler.addCommand("OPEN", openIris);
    SerialCommandHandler.addCommand("HOME", homeIris);
    SerialCommandHandler.addCommand("GOTO", handle_goToPosition);
    SerialCommandHandler.addCommand("POS", queryPosition);
    // init Iris stuff
    pinMode(closedpin, INPUT_PULLUP);
    pinMode(openedpin, INPUT_PULLUP);
    pinMode(closedpin2, INPUT_PULLUP);
    pinMode(openedpin2, INPUT_PULLUP);
    iris.setSpeed(10); //rpm

    // LED for funsies
    pinMode(LED_BUILTIN, OUTPUT);
    pinMode(en_1, OUTPUT);
    pinMode(en_2, OUTPUT);
    digitalWrite(en_1, LOW);
    digitalWrite(en_2, LOW);
    Serial.println("Booted");
}


void loop() {
    // Process incoming commands
    SerialCommandHandler.processSerial(Serial);

    // Other loop tasks
}

bool select_iris(int iris_sel){
  // Serial.println(iris_sel);
  if (iris_sel == 1){
    digitalWrite(en_2, LOW);
    digitalWrite(en_1, HIGH);
    return true;
  }
  else if (iris_sel == 2){
    digitalWrite(en_1, LOW);
    digitalWrite(en_2, HIGH);
    return true;
  }
  else{
    // shouldn't get here unless shit is fucked
    digitalWrite(en_1, LOW);
    digitalWrite(en_2, LOW);
    return false;
  }
}

void homeIris(){
  int iris_sel;
  iris_sel = SerialCommandHandler.readIntArg();
  if (select_iris(iris_sel)){
    if (iris_sel == 1){
        int tmp = 0;
        // open first:
        while (digitalRead(openedpin) != 0){
          iris.step(-stepamount);
          tmp += stepamount;
          if (tmp > 1600){
            Serial.println("NC");
            return;
          }
        }
        // we are fully open now
        int totalsteps = 0;
        while (digitalRead(closedpin) != 0){
          iris.step(stepamount);
          totalsteps += stepamount;
        }
        iris.step(-stepamount);

        closedPosition_1 = totalsteps;
        currentPosition_1 = totalsteps;
        isHomed_1 = true;
        // Serial.println("OK");
        goToPosition(currentPosition_1 / 2, iris_sel);
    }

    else{
        // open first:
        int tmp = 0;
        while (digitalRead(openedpin2) != 0){
          iris.step(-stepamount);
          tmp += stepamount;
          if (tmp > 1600){
            Serial.println("NC");
            return;
          }
        }
        // we are fully open now
        int totalsteps = 0;
        while (digitalRead(closedpin2) != 0){
          iris.step(stepamount);
          totalsteps += stepamount;
        }
        iris.step(-stepamount);

        closedPosition_2 = totalsteps;
        currentPosition_2 = totalsteps;
        isHomed_2 = true;
        // Serial.println("OK");
        goToPosition(currentPosition_2 / 2, iris_sel);
    }
    
  }
  else{
    Serial.println("Error: Homing Failed");
  }
  disable_steppers();
}

void closeIris(){
  int iris_sel;
  iris_sel = SerialCommandHandler.readIntArg();
  if (select_iris(iris_sel)){
      if (iris_sel == 1){
        if (!isHomed_1){
          Serial.println("Home first!");
        }
        else {
          int totalsteps = 0;
          while (digitalRead(closedpin) != 0 && totalsteps <= 1300){
              iris.step(stepamount);
              totalsteps += stepamount;
            } 
          if (totalsteps > 1300) {
              Serial.println("Error");
          }
          else{
              Serial.println("OK");
              currentPosition_1 = closedPosition_1;
          }
      
      }
      }
        else{
          if (!isHomed_2){
            Serial.println("Home first!");
            }
          else {
              int totalsteps = 0;
              while (digitalRead(closedpin2) != 0 && totalsteps <= 1300){
                iris.step(stepamount);
                totalsteps += stepamount;
              } 
            if (totalsteps > 1300) {
                Serial.println("Error");
              }
              else{
                // iris.step(-100);
                Serial.println("OK");
              currentPosition_2 = closedPosition_2;
            }
        } 
      }
    }
  else{
    Serial.println("Error");
  }
  disable_steppers();
}

void openIris(){
  int iris_sel;
  iris_sel = SerialCommandHandler.readIntArg();
  if (select_iris(iris_sel)){
      if (iris_sel == 1){
        if (!isHomed_1){
          Serial.println("Home first!");
        }
        else {
          int totalsteps = 0;
          while (digitalRead(openedpin) != 0 && totalsteps <= 1300){
              iris.step(-stepamount);
              totalsteps += stepamount;
            } 
          if (totalsteps > 1300) {
              Serial.println("Error");
          }
          else{
              Serial.println("OK");
              currentPosition_1 = openPosition_1;
          }
      
      }
      }
        else{
          if (!isHomed_2){
            Serial.println("Home first!");
            }
          else {
              int totalsteps = 0;
              while (digitalRead(openedpin2) != 0 && totalsteps <= 1300){
                iris.step(-stepamount);
                totalsteps += stepamount;
              } 
            if (totalsteps > 1300) {
                Serial.println("Error");
              }
              else{
                // iris.step(-100);
                Serial.println("OK");
              currentPosition_2 = openPosition_2;
            }
        } 
      }
    }
  else{
    Serial.println("Error");
  }
  disable_steppers();
}

void handle_goToPosition(){
  int iris_sel;
  iris_sel = SerialCommandHandler.readIntArg(); 
  float pos;
  pos = SerialCommandHandler.readFloatArg();
  if (iris_sel == 1){
    int steppos = mapFloat(pos, 41.3, 2.0, 0, closedPosition_1);
    if (SerialCommandHandler.argOk){
      goToPosition(steppos, iris_sel);
    }
  }
  else{
    int steppos = mapFloat(pos, 41.3, 2.0, 0, closedPosition_2);
    if (SerialCommandHandler.argOk){
      goToPosition(steppos, iris_sel);
  }
  }
  disable_steppers();
}

void queryPosition(){
  int iris_sel;
  iris_sel = SerialCommandHandler.readIntArg();
  float rtn = 0.0;
  if (iris_sel == 1){
    rtn = mapFloat(currentPosition_1, 0, (float)closedPosition_1, 41.3, 2.0);
  }
  else{
    rtn = mapFloat(currentPosition_2, 0, (float)closedPosition_2, 41.3, 2.0);
  }

  Serial.println(rtn);
}


void goToPosition(int pos, int iris_sel){
  if (select_iris(iris_sel)){
    if (iris_sel == 1){
          if (!isHomed_1){
          Serial.println("Home first!1");
        }
        else{
          if (pos > closedPosition_1 || pos < 0){
            Serial.println("Error Out of Bounds");
          }
          else{
            iris.step(-(currentPosition_1 - pos));
          }
          currentPosition_1 = currentPosition_1 - (currentPosition_1 - pos);
          Serial.println("OK");
        }
      }
      else{
          if (!isHomed_2){
            Serial.println("Home first!2");
          }
          else{
            if (pos > closedPosition_2 || pos < 0){
              Serial.println("Error Out of Bounds");
            }
            else{
              iris.step(-(currentPosition_2 - pos));
            }
            currentPosition_2 = currentPosition_2 - (currentPosition_2 - pos);
            Serial.println("OK");
        }
       }
    }
    else{
      Serial.println("Error");
    }
    disable_steppers();
}

void HandleLEDCommand() {
  char *cmd;
  cmd = SerialCommandHandler.readStringArg();
  Serial.println(cmd);
  if (strcmp(cmd, "ON") == 0){
        digitalWrite(LED_BUILTIN, HIGH);
        Serial.println("LED turned ON");
  }
  
  else if (strcmp(cmd, "OFF") == 0){
        digitalWrite(LED_BUILTIN, LOW);
        Serial.println("LED turned OFF");
  }
  else {
    Serial.println("Unknown LED State");
  }
}

float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
  return (float)((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min);
}
// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command) {
  Serial.println("Recognized Commands are OPEN; CLOSE; HOME; GOTO; and LED;");
}

void disable_steppers(){
  digitalWrite(en_1, LOW);
  digitalWrite(en_2, LOW);
}
