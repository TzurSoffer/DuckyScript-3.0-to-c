# Convertor: DuckyScript to Arduino Converter

## Overview
The **Convertor** class is a Python-based script that converts DuckyScript into Arduino code for keyboard emulation. It is the only converter that supports DuckyScript 3.0 as far as I am aware. This enables more complex operations then before.

## Features
- Support for **DuckyScript 3.0** commands.
- Converts DuckyScript into Arduino-compatible `.ino` files.
- Dynamic variable and constant definitions.
- Function support.
- Advanced logic handling with `IF`, `WHILE`, and conditional blocks.
- Keyboard press, release, and delay management.
- Support for custom keyboard layouts via JSON configuration.

## Requirements
- Python 3.6 or higher
- An Arduino-compatible device with support for `Keyboard.h` (e.g., Arduino Leonardo or Arduino Micro)

## Installation
1. Clone the repository or download the script.
2. Ensure Python is installed on your system.

## Usage
### Input Script Format
The input script should be a text file written in DuckyScript 3.0 format. Each command corresponds to a specific action. Supported commands include:

| Command                | Description                                         |
|------------------------|-----------------------------------------------------|
| `REM <comment>`        | Comment                                             |
| `REM_BLOCK <comment>`  | Comment block, comment until END_REM                |
| `END_REM`              | End REM_BLOCK                                       |
| `DELAY <time>`         | Adds a delay in milliseconds.                       |
| `STRING <text>`        | Types a string using the keyboard.                  |
| `STRINGLN <text>`      | Types a string followed by `ENTER`.                 |
| `HOLD <key>`           | Holds down a key.                                   |
| `RELEASE <key>`        | Releases a key.                                     |
| `DEFAULT_DELAY <time>` | Sets the default delay for all commands.            |
| `STRINGDELAY <time>`   | Sets the delay between characters in strings.       |
| `VAR $name value`      | Defines a variable.                                 |
| `DEFINE #name value`   | Defines a constant.                                 |
| `WHILE <condition>`    | Starts a `while` loop.                              |
| `FUNCTION <name>`      | declares a function that will execute once called.  |
| `IF <condition>`       | Starts an `if` block.                               |
| `END_WHILE`, `END_IF`, `END_FUNCTION`  | Ends a `while` / `if` / `function` block.  |
| `RESET`                | Releases all keys.                                  |
| `RESTART_PAYLOAD`      | Restarts the script.                                |
| `STOP_PAYLOAD`         | Stops the script.                                   |

### Example Input Script (`payload.txt`)
```txt
REM_BLOCK
Example Script
Just a simple script to be converted to c
END_REM

DEFINE #message textMessage
VAR $count = 5

GUI r
delay 1000
STRINGLN notepad.exe
delay 1000

FUNCTION TIMER()
WHILE ($count > 0)
    STRINGLN $count
    $count -= 1
    delay 1000
END_WHILE
END_FUNCTION

TIMER()
$count = 3
TIMER()
$count = 2
TIMER()
$count = 10
TIMER()

STRINGLN Timer ended
```

### Running the Script
1. Place the input script (e.g., `payload.txt`) in the same directory as the Python script.
2. Run the script:
   ```bash
   python convertor.py
   ```
3. The converted Arduino code will be printed to the console and saved to `output.ino`.

## API Documentation
### `Convertor` Class
#### `__init__(self, script, layout="US")`
Initializes the Convertor.
- **script**: Path to the input script file.
- **layout**: Keyboard layout to use (default: `US`).

#### `convert(self)`
Converts the input script into Arduino code and stores it in `self.arduinoOutput`.

#### `save(self, filename, code=None)`
Saves the generated Arduino code to a file.
- **filename**: Output file name (e.g., `output.ino`).
- **code**: Optional; Arduino code to save (default: `self.arduinoOutput`).

## Extending the Script
You can add new commands by extending the `self.commands` dictionary in the `Convertor` class and defining corresponding methods. For example:
```python
self.commands["NEW_COMMAND"] = self._newCommand

def _newCommand(self, arg):
    return f"// Custom command with {arg}"
```

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Support
For questions or issues, open an issue on the repository.