#include <CommandHandler.h>
#include <Stepper.h>
CommandHandler SerialCommandHandler(" ", ';');

// stepper init
const int stepsPerRevolution = 2038;
int currentPosition = 0;
int openPosition = 0;
int closedPosition = 0;
bool isHomed = false;
Stepper iris = Stepper(stepsPerRevolution, 8, 10, 9, 11);
const int closedpin = 6;
const int openedpin = 5;
const int stepamount = 25;
void setup() {
    // Initialize serial communication
    Serial.begin(115200);
    SerialCommandHandler.setCmdHeader("FEEDBACK");
    SerialCommandHandler.addCommand("LED", HandleLEDCommand);
    SerialCommandHandler.setDefaultHandler(unrecognized);
    SerialCommandHandler.addCommand("CLOSE", closeIris);
    SerialCommandHandler.addCommand("OPEN", openIris);
    SerialCommandHandler.addCommand("HOME", homeIris);
    SerialCommandHandler.addCommand("GOTO", handle_goToPosition);
    SerialCommandHandler.addCommand("POS", queryPosition);
    // init Iris stuff
    pinMode(closedpin, INPUT_PULLUP);
    pinMode(openedpin, INPUT_PULLUP);
    iris.setSpeed(10); //rpm
    // LED for funsies
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.println("Booted");
    }


void loop() {
    // Process incoming commands
    SerialCommandHandler.processSerial(Serial);

    // Other loop tasks
}
void homeIris(){
  // open first:
  while (digitalRead(openedpin) != 0){
    iris.step(-stepamount);
  }
  // we are fully open now
  int totalsteps = 0;
  while (digitalRead(closedpin) != 0){
    iris.step(stepamount);
    totalsteps += stepamount;
  }
  iris.step(-stepamount);

  closedPosition = totalsteps;
  currentPosition = totalsteps;
  isHomed = true;
  // Serial.println("OK");
  goToPosition(currentPosition / 2);
}

void closeIris(){
  if (!isHomed){
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
      // iris.step(-100);
      Serial.println("OK");
    }
    currentPosition = closedPosition;
  }
}

void openIris(){
  if (!isHomed){
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
      // iris.step(100);
      Serial.println("OK");
    }
    currentPosition = 0;
  }
}
void handle_goToPosition(){
  float pos;
  pos = SerialCommandHandler.readFloatArg();
  int steppos = mapFloat(pos, 41.3, 2.0, 0, closedPosition);
  if (SerialCommandHandler.argOk){
    goToPosition(steppos);
  }
}

void queryPosition(){
  float rtn = mapFloat(currentPosition, 0, (float)closedPosition, 41.3, 2.0);
  Serial.println(rtn);

}


void goToPosition(int pos){
  if (!isHomed){
    Serial.println("Home first!");
  }
  else{
    if (pos > closedPosition || pos < 0){
      Serial.println("Error Out of Bounds");
    }
    else{
      // Serial.print("Current Position: ");
      // Serial.print(currentPosition);
      // Serial.print(" Going to: ");
      // Serial.println(pos);
      iris.step(-(currentPosition - pos));
    }
    currentPosition = currentPosition - (currentPosition - pos);
    Serial.println("OK");
  }
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

