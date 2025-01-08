import json
import inspect
import re
from ast import literal_eval

def detectType(text):
    try:
        _type = type(literal_eval(text))
        if _type == str:
            return("String")
        if _type == int:
            return("int")
        if _type == float:
            return("float")
        if _type == bool:
            return("bool")

    except (ValueError, SyntaxError):
            return("String")

def getArgsKwargs(func):
    signature = inspect.signature(func)
    parameters = signature.parameters

    args = [param for param in parameters.values() if param.default == inspect.Parameter.empty]
    kwargs = [param for param in parameters.values() if param.default != inspect.Parameter.empty]

    return(len(args), len(kwargs))

class Convertor:
    def __init__(self,  script):
        self.commands = {
            "DELAY": self._delay,
            "STRING": self._string,
            "STRINGLN": self._stringln,
            "HOLD": self._keyDown,
            "RELEASE": self._keyUp,
            "DEFAULT_DELAY": self._setDefaultDelay,
            "DEFAULTDELAY": self._setDefaultDelay,
            "STRINGDELAY": self._setStringDelay,
            "VAR": self._setVar,
            "DEFINE": self._setDefine,
            "WHILE": self._startWhile,
            "ENDWHILE": self._endFunc,
            "END_WHILE": self._endFunc,
            "IF": self._startIf,
            "ENDIF": self._endFunc,
            "END_IF": self._endFunc,
            "ELSE": self._startElse,
            "RESET": self._releaseAll,
            "RESTART_PAYLOAD": self._restart,
            "STOP_PAYLOAD": self._stop
        }
        
        self.vars = {}
        self.defines = {}
        
        self.defaultDelay = 10
        self.stringDelay = 5

        self.nestDeepness = 0

        self.arduinoOutput = ""

        with open(script) as f:
            self.script = f.read()
        with open(f"keyConversion.json") as f:
            self.layout = json.load(f)

    def _removeTHEN(self, condition):
        return(condition[:condition.rfind(" THEN")])

    def _createVar(self, varName, value):
        varType = detectType(value)
        if varType == "String":
            value = f'"{value}"'
        return(f"{varType} {varName} = {value};")

    def _keyDown(self, key):
        if key.upper() not in self.layout:
            return(f"Keyboard.press('{key}');")
        return(f"Keyboard.press({self.layout[key.upper()]});")
    
    def _keyUp(self, key):
        if key.upper() not in self.layout:
            return(f"Keyboard.release('{key}');")
        return(f"Keyboard.release({self.layout[key.upper()]});")
    
    def _releaseAll(self):
        return(f"Keyboard.releaseAll();")
    
    def _delay(self, time=None):
        if time is None:
            time = self.defaultDelay
        return(f"delay({time});")

    def _setDefaultDelay(self, time):
        self.defaultDelay = time
        return("")
    
    def _setStringDelay(self, time):
        self.stringDelay = time/1_000_000       #< in nanoseconds
        return("")

    def _pressKey(self, key):
        key = key.upper()
        return(f"{self._keyDown(key)}\n{self._delay(10)}\n{self._keyUp(key)}")

    def _string(self, text):
        newText = "\""
        words = text.split(" ")
        for word in words:
            if word in self.vars or word in self.defines:
                newText += f'" + String({word}) + " '
            else:
                trimmedWord = word.replace('\\', '')
                if trimmedWord in self.vars or trimmedWord in self.defines:
                    word = trimmedWord
                newText += f"{word} "
        if newText.endswith(' + " '):                    #< cant be apart of the string do to all " being replaced with \"
            newText = newText[:-5]
        else:
            newText = newText[:-1]+"\""
        return(f"typeWithDelay({newText}, {self.stringDelay});")

    def _stringln(self, text):
        return(f"{self._string(text)}\n{self._pressKey("ENTER")}")

    def _setVar(self, expression):
        expression = expression[1:]
        match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', expression)
        if match:
            varName = match.group(1)

        self.vars[varName] = expression
        varType = detectType(expression[expression.rfind(" ")+1:])
        return(f"{varType} {expression};")

    def _setDefine(self, defineName, value):
        self.defines[defineName[1:]] = value
        return(self._createVar(defineName[1:], value))
    
    def _startWhile(self, condition):
        self.nestDeepness += 1
        return(f"while({condition}) "+"{")

    def _startIf(self, condition):
        self.nestDeepness += 1
        return(f"if({self._removeTHEN(condition)}) "+"{")

    def _startElse(self, condition=None):
        if condition is None:
            return("} else "+"{")
        condition = self._removeTHEN(condition)
        if condition.upper().startswith("IF"):
            condition = condition[2:]
        return("}" + f"else if({condition}) "+"{")

    def _endFunc(self):
        print(self.nestDeepness)
        for _ in range(self.nestDeepness-1):
            self.addLine("}")
        self.nestDeepness = 0
        return("}")

    def _restart(self):
        return("goto start;")

    def _stop(self):
        return("goto end;")

    def addLine(self, line):
        self.arduinoOutput += f"{line}\n"

    def _addPreCode(self):

        self.addLine("#include <Keyboard.h>")

        self.addLine("void typeWithDelay(String text, int delayTime) {")
        self.addLine("for (int i = 0; i < text.length(); i++) {")
        self.addLine("Keyboard.press(text[i]);")
        self.addLine("delay(delayTime);")
        self.addLine("Keyboard.release(text[i]);")
        self.addLine("}}")

        self.addLine("void setup() {")
        self.addLine("Keyboard.begin();")

        self.addLine("start:")
        self.addLine("delay(1000);")
    
    def _addPostCode(self):
        self.addLine("end:")
        self.addLine("Keyboard.end();")
        self.addLine("}")
        self.addLine("void loop() {}")

    def convert(self):
        self._addPreCode()
        scriptIter = iter(self.script.split("\n"))
        for line in scriptIter:
            line = line.strip()
            if line.startswith("REM_BLOCK"):
                while line != "END_REM":
                    line = next(scriptIter)
                    line = line.strip()
            if line == "" or line.startswith("REM"):     #< ignore empty lines
                continue
            line = line.replace('"', '\\"')
            line = line.replace('\\', '\\\"')

            for var in self.vars.keys():
                line = line.replace(var, f"\\{var}")
                line = line.replace(f"$\\{var}", var)
                if line.startswith(var):
                    self.addLine(line+";")

            for define in self.defines.keys():
                line = line.replace(define, f"\\{define}")
                line = line.replace(f"#\\{define}", define)
                if line.startswith(define):
                    self.addLine(line+";")

            lineFrag = line.split(" ")
            if lineFrag[0].upper() in self.layout or (lineFrag[0].isalpha() and len(lineFrag[0]) == 1):
                for key in lineFrag:
                    upperKey = key.upper()
                    if upperKey in self.layout:
                        self.addLine(self._keyDown(upperKey))
                        self.addLine(self._delay(10))
                    else:
                        self.addLine(self._keyDown(key))
                for key in reversed(lineFrag):
                    upperKey = key.upper()
                    if upperKey in self.layout:
                        self.addLine(self._keyUp(upperKey))
                        self.addLine(self._delay(10))
                    else:
                        self.addLine(self._keyUp(key))
            elif lineFrag[0].upper() in self.commands:
                command = lineFrag[0].upper()
                vars = lineFrag[1:]
                lineVarLength = len(vars)
                method = self.commands[command]
                argsLen, kwargsLen = getArgsKwargs(method)
                if argsLen + kwargsLen == 0:
                    self.addLine(method())

                elif argsLen + kwargsLen == 1:                     #< for funcs that need a string (STRING/STRINGLN)
                    self.addLine(method(line[line.find(" ")+1:]))
                
                elif lineVarLength >= argsLen and lineVarLength <= argsLen + kwargsLen:
                    self.addLine(method(*vars))

            self.addLine(self._delay(self.defaultDelay))

        self._addPostCode()
        return(self.arduinoOutput)
    
    def save(self, filename, code=None):
        if code == None:
            code = self.arduinoOutput
        with open(filename, "w") as f:
            f.write(code)

if __name__ == "__main__":
    c = Convertor("payload.txt")
    c.convert()
    print(c.arduinoOutput)
    c.save("output.ino")