#include <Keyboard.h>
int count = 5;
String message = "textMessage";
int _JITTER_MAX = 10;
int _JITTER_MIN = 5;
bool _JITTER_ENABLED = false;
bool TRUE = true;
bool FALSE = false;
bool True = true;
bool False = false;
void typeWithDelay(String text) {
for (int i = 0; i < text.length(); i++) {
int TIMER(){
while((count > 0)) {
typeWithDelay("" + String(count));
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
count -= 1;
delay(1000);
}
return (int)true;
}
Keyboard.press(text[i]);
if (_JITTER_ENABLED == true) {
delay(random(_JITTER_MIN, _JITTER_MAX));
} else {
delay(_JITTER_MIN);
}
Keyboard.release(text[i]);
}}
void setup() {
Keyboard.begin();
start:
delay(1000);


Keyboard.press(KEY_LEFT_GUI);
delay(10);
delay(10);
Keyboard.press('r');
Keyboard.release('r');
Keyboard.release(KEY_LEFT_GUI);
delay(10);
delay(10);
delay(10);
delay(1000);
typeWithDelay("notepad.exe");
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
delay(1000);

typeWithDelay("" + String(TIMER()));
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
count = 3;
TIMER();
typeWithDelay("Timer ended");
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
end:
Keyboard.end();
}
void loop() {}
