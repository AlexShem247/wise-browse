import sys
import re
import base64

from PyQt5.QtWidgets import QApplication
from PyQt5.uic import compileUi


def convert_ui_to_py(ui_file_path, py_file_path):
    with open(ui_file_path, "r") as ui_file:
        with open(py_file_path, "w") as py_file:
            compileUi(ui_file, py_file)


def removeLocalImports(file_contents):
    lines = file_contents.split('\n')
    filtered_lines = []

    # Regex to match local imports (e.g., "from src import ...")
    local_import_pattern = re.compile(r'^\s*from\s+src(\.|$|\s)')

    for line in lines:
        if not local_import_pattern.match(line):
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)


def blockComment(text):
    return f"{'#' * 80}\n# {text}\n{'#' * 80}\n"


def contents(file):
    with (open(file) as g):
        fileContents = removeLocalImports(g.read()
                                          ).replace("uic.loadUi(self.UI_FILE, self)",
                                                    "self.ui = Ui_MainWindow()\n        self.ui.setupUi(self)\n")
        return f"{blockComment(file)}{fileContents}\n"


def encode_png_to_base64(png_file_path):
    with open(png_file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


DECODE_FUNC = """
import base64
from pathlib import Path

def decode_base64_to_png(encoded_string, file_path):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)  
    
    with open(file_path, "wb") as output_file:
        output_file.write(base64.b64decode(encoded_string))

"""


def writeImg(file):
    return f'{getVarName(file)} = "{encode_png_to_base64(file)}"\n'


def getVarName(file):
    return file.split("/")[-1].split(".")[0].upper() + "_PNG_CONTENTS"


IF_MAIN = 'if __name__ == "__main__":'

IMG_FILES = ["assets/img/clipboard.png"
    , "assets/img/home.png"
    , "assets/img/internet.png"
    , "assets/img/microphone.png"
    , "assets/img/settings.png"
    , "assets/img/star_empty.png"
    , "assets/img/star_filled.png"]

if __name__ == "__main__":
    convert_ui_to_py("assets/UI/MainPage.ui", "temp/MainPage.py")
    with open("output.py", "w") as f:
        f.write(blockComment("Writing Image Files"))
        for img in IMG_FILES:
            f.write(writeImg(img))
        f.write("\n")

        f.write(contents("temp/MainPage.py"))
        f.write(contents("src/Assistant.py"))
        f.write(contents("src/EventFilters.py"))
        f.write(contents("src/FAQDatabase.py"))
        f.write(contents("src/URLUtils.py"))
        f.write(contents("src/WebBrowser.py"))

        f.write(DECODE_FUNC)
        steps = [f"decode_base64_to_png({getVarName(file)}, '{file}')" for file in IMG_FILES]
        main = contents("main.py")
        f.write(main.replace(IF_MAIN, IF_MAIN + "\n    " + "\n    ".join(steps)))
