#include <Keyboard.h>
int count = 5;
String message = "textMessage";
void typeWithDelay(String text, int delayTime) {
for (int i = 0; i < text.length(); i++) {
Keyboard.press(text[i]);
delay(delayTime);
Keyboard.release(text[i]);
}}
int TIMER(){
while((count > 0)) {
typeWithDelay("" + String(count), 5);
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
typeWithDelay("notepad.exe", 5);
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
delay(1000);

typeWithDelay("" + String(TIMER()), 5);
delay(10);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(10);
count = 3;
TIMER();
count = 2;
TIMER();
count = 10;
TIMER();
typeWithDelay("Timer ended", 5);
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
