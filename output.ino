#include <Keyboard.h>
void typeWithDelay(String text, int delayTime) {
for (int i = 0; i < text.length(); i++) {
Keyboard.press(text[i]);
delay(delayTime);
Keyboard.release(text[i]);
}}
void setup() {
Keyboard.begin();
start:
delay(1000);
delay(10);
String message = "textMessage";
delay(10);
int count = 5;
delay(10);
Keyboard.press(KEY_LEFT_GUI);
delay(10);
Keyboard.press('r');
Keyboard.release('r');
Keyboard.release(KEY_LEFT_GUI);
delay(10);
delay(10);
delay(1000);
delay(10);
typeWithDelay("notepad.exe", 5);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
delay(1000);
delay(10);
while((count > 0)) {
delay(10);
typeWithDelay("" + String(count), 5);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
count -= 1;
delay(10);
delay(1000);
delay(10);
}
delay(10);
typeWithDelay("Timer ended", 5);
Keyboard.press(KEY_KP_ENTER);
delay(10);
Keyboard.release(KEY_KP_ENTER);
delay(10);
end:
Keyboard.end();
}
void loop() {}
