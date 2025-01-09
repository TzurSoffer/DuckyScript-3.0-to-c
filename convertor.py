import json
import inspect
import re
from ast import literal_eval

def detectType(text):
    try:
        _type = type(literal_eval(text.lower().capitalize()))     #< Check for bool by converting TRUE/FALSE to True/False
        if _type == bool:
            return("bool")
        _type = type(literal_eval(text))
        if _type == str:
            return("String")
        if _type == int:
            return("int")
        if _type == float:
            return("float")

    except (ValueError, SyntaxError):
            return("String")

def getArgsKwargs(func):
    signature = inspect.signature(func)
    parameters = signature.parameters

    args = [param for param in parameters.values() if param.default == inspect.Parameter.empty]
    kwargs = [param for param in parameters.values() if param.default != inspect.Parameter.empty]

    return(len(args), len(kwargs))

class Convertor():
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
            "STOP_PAYLOAD": self._stop,
            "FUNCTION": self._createFunction
        }

        self.vars = {}
        self.defines = {}
        self.functions = {}

        self.defaultDelay = 10
        self.stringDelay = 5
        
        self.absoluteStart = 2
        self.functionsStart = 8

        self.arduinoOutput = ""

        with open(script) as f:
            self.script = f.read()
            self.scriptIter = iter(self.script.split("\n"))

        with open(f"keyConversion.json") as f:
            self.keyConversion = json.load(f)

    def _removeTHEN(self, condition):
        return(condition[:condition.rfind(" THEN")])

    def _addStringToBeginning(self, stringToAdd, location=None):
        if location == None:
            location = self.functionsStart

        lines = self.arduinoOutput.split('\n')

        # Modify the specific line
        lines[location-1] = stringToAdd + "\n" + lines[location-1]

        # Join the lines back into a single string
        arduinoOutput = '\n'.join(lines)
        return(arduinoOutput)
    
    def _addVariableToOutput(self, expression):
        self.functionsStart += 1
        return(self._addStringToBeginning(expression, 2))

    def _getCodeBlock(self, endPhrase):
        block = ""
        _break = False

        if type(endPhrase) == str:
            endPhrase = [endPhrase.upper()]
        else:
            endPhrase = [phrase.upper() for phrase in endPhrase]

        for line in self.scriptIter:
            _line = line.strip().upper()
            for phrase in endPhrase:
                if _line == phrase:
                    _break = True
                    break
            if _break:
                break
            block += line+"\n"
        return(block[:-1])
    
    def _createFunction(self, name):
        arduCode = ""
        type = "void"
        name = name.strip().replace("()", "")
        code = self._getCodeBlock(["END_FUNCTION", "ENDFUNCTION"])
        lines = code.split("\n")
        
        for line in lines:
            if line.strip().startswith("RETURN"):
                type = "int"
                arduCode += self._return(line.removeprefix("RETURN").strip().lower())
            else:
                arduCode += self.convertLine(line)

        arduCode = f"{type} {name}()" + "{\n" + arduCode + "\n}"

        self.functions[name] = arduCode
        self.arduinoOutput = self._addStringToBeginning(arduCode)
        return("")
    
    def _return(self, value):
        return(f"return (int){value};")
    
    def _isVar(self, text):
        if text in self.vars:
            return(True)
        return(False)

    def _isDefine(self, text):
        if text in self.defines:
            return(True)
        return(False)

    def _createVar(self, varName, value):
        varType = detectType(value)
        if varType == "String":
            value = f'"{value}"'
        self.arduinoOutput = self._addVariableToOutput(f"{varType} {varName} = {value};")
        return("")

    def _keyDown(self, key):
        if key.upper() not in self.keyConversion:
            return(f"Keyboard.press('{key}');")
        return(f"Keyboard.press({self.keyConversion[key.upper()]});\n{self._delay(self.defaultDelay)}")
    
    def _keyUp(self, key):
        if key.upper() not in self.keyConversion:
            return(f"Keyboard.release('{key}');")
        return(f"Keyboard.release({self.keyConversion[key.upper()]});\n{self._delay(self.defaultDelay)}")
    
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
        return(f"{self._keyDown(key)}\n{self._keyUp(key)}")

    def _string(self, text):
        newText = "\""
        words = text.split(" ")
        for word in words:
            print(word.removesuffix("()"))
            if word in self.vars or word in self.defines or word.removesuffix("()") in self.functions:
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
        return(f"typeWithDelay({newText}, {self.stringDelay});\n{self._delay(self.defaultDelay)}")

    def _stringln(self, text):
        return(f"{self._string(text)}\n{self._pressKey("ENTER")}\n{self._delay(self.defaultDelay)}")

    def _setVar(self, expression):
        expression = expression[1:]
        match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', expression)
        if match:
            varName = match.group(1)

        self.vars[varName] = expression
        varType = detectType(expression[expression.rfind(" ")+1:])
        self.arduinoOutput = self._addVariableToOutput(f"{varType} {expression};")
        return("")

    def _setDefine(self, defineName, value):
        self.defines[defineName[1:]] = value
        return(self._createVar(defineName[1:], value))

    def _startWhile(self, condition):
        return(f"while({condition}) "+"{")

    def _startIf(self, condition):
        return(f"if({self._removeTHEN(condition)}) "+"{")

    def _startElse(self, condition=None):
        if condition is None:
            return("} else "+"{")
        condition = self._removeTHEN(condition)
        if condition.upper().startswith("IF"):
            condition = condition[2:]
        return("}" + f"else if({condition}) "+"{")

    def _endFunc(self):
        return("}")

    def _restart(self):
        return("goto start;")

    def _stop(self):
        return("goto end;")

    def addLine(self, line, text="self", end="\n"):
        newline = f"{line}{end}"
        if text != None:
            self.arduinoOutput += newline
        return(newline)

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
    
    def convertLine(self, line):
        newLine = ""
        line = line.strip()
        if line.startswith("REM_BLOCK"):                  #< Ignore comments
            while line != "END_REM":
                line = next(self.scriptIter)
                line = line.strip()
        if line == "" or line.startswith("REM"):          #< ignore empty lines and comments
            return("")

        line = line.replace('"', '\\"')
        line = line.replace('\\', '\\\"')

        for var in self.vars.keys():
            line = line.replace(var, f"\\{var}")          #<  replace all instance of a varName with /varName
            line = line.replace(f"$\\{var}", var)         #<  replace all instance of a variable with its name (varName)
            if line.startswith(var):
                newLine += self.addLine(line+";", text=None)

        for define in self.defines.keys():
            line = line.replace(define, f"\\{define}")    #<  replace all instance of a defineName with /defineName
            line = line.replace(f"#\\{define}", define)   #<  replace all instance of a define with its name (defineName)
            if line.startswith(define):
                newLine += self.addLine(line+";", text=None)

        lineFrag = line.split(" ")
        
        if lineFrag[0].removesuffix("()") in self.functions:
            newLine += self.addLine(f"{lineFrag[0]};", text=None)
            return(newLine)
        
        if (lineFrag[0].upper() in self.keyConversion) or (lineFrag[0].isalpha() and len(lineFrag[0]) == 1):    #< check if its a letter or key
            for key in lineFrag:
                upperKey = key.upper()
                if upperKey in self.keyConversion:
                    newLine += self.addLine(self._keyDown(upperKey), text=None)
                    newLine += self.addLine(self._delay(10), text=None)
                else:
                    newLine += self.addLine(self._keyDown(key), text=None)
            for key in reversed(lineFrag):
                upperKey = key.upper()
                if upperKey in self.keyConversion:
                    newLine += self.addLine(self._keyUp(upperKey), text=None)
                    newLine += self.addLine(self._delay(10), text=None)
                else:
                    newLine += self.addLine(self._keyUp(key), text=None)
            newLine += self.addLine(self._delay(self.defaultDelay), text=None)

        elif lineFrag[0].upper() in self.commands:            #< check if its a command
            command = lineFrag[0].upper()
            vars = lineFrag[1:]
            lineVarLength = len(vars)
            method = self.commands[command]
            argsLen, kwargsLen = getArgsKwargs(method)
            if argsLen + kwargsLen == 0:
                newLine += self.addLine(method(), text=None)

            elif argsLen + kwargsLen == 1:                     #< for funcs that need a string (STRING/STRINGLN)
                newLine += self.addLine(method(line[line.find(" ")+1:]), text=None)
            
            elif lineVarLength >= argsLen and lineVarLength <= argsLen + kwargsLen:
                newLine += self.addLine(method(*vars), text=None)
        
        return(newLine)

    def convert(self):
        self._addPreCode()
        for line in self.scriptIter:
            self.addLine(self.convertLine(line), end="")

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