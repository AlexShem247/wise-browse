import base64
import re
import tempfile
import os
import subprocess
import shutil
from pathlib import Path

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


def replaceImageReferences(fileContents):
    pattern = r'Path\("assets/img/([a-zA-Z0-9_]+)\.png"\)'

    def replacement_function(match):
        img_name = match.group(1).upper()
        return f'Path({img_name}_PNG)'

    return re.sub(pattern, replacement_function, fileContents)


def contents(file):
    with (open(file) as g):
        fileContents = removeLocalImports(g.read()
                                          ).replace("uic.loadUi(self.UI_FILE, self)",
                                                    "self.ui = Ui_MainWindow()\n        self.ui.setupUi(self)\n")
        return f"{blockComment(file)}{replaceImageReferences(fileContents)}\n"


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
    return os.path.splitext(os.path.basename(file))[0].upper() + "_PNG_CONTENTS"


def execute_command(*command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Read and print the output in real-time
    for line in process.stdout:
        print(line, end='')

    # Wait for the process to complete and get the return code
    return_code = process.wait()

    # Read and print any remaining output from stderr
    for line in process.stderr:
        print(line, end='')

    return return_code


IF_MAIN = 'if __name__ == "__main__":'

PROGRAM_NAME = "Wise Browse"

IMG_FILES = [str(Path("assets") / "img" / f) for f in os.listdir("assets/img") if f.endswith(".png")]
SRC_FILES = [str(Path("src") / f) for f in os.listdir("src") if f.endswith(".py")]

if __name__ == "__main__":
    outputFile, outputFilename = tempfile.mkstemp()
    with open(outputFilename, "w") as f:
        # Add Images
        f.write(blockComment("Writing Image Files"))
        f.write("import tempfile\n\n")
        for img in IMG_FILES:
            f.write(writeImg(img))
            f.write(f"_, {getVarName(img).replace('_CONTENTS', '')} = tempfile.mkstemp()\n")
        f.write("\n")

        # Add UI File
        uiFile, uiFilename = tempfile.mkstemp()
        convert_ui_to_py("assets/UI/MainPage.ui", uiFilename)
        f.write(contents(uiFilename))
        os.close(uiFile)

        # Add src .py files
        for file in SRC_FILES:
            f.write(contents(file))

        # Add main.py
        f.write(DECODE_FUNC)
        steps = [f"decode_base64_to_png({getVarName(file)}, {getVarName(file).replace('_CONTENTS', '')})"
                 for file in IMG_FILES]
        main = contents("main.py")
        f.write(main.replace(IF_MAIN, IF_MAIN + "\n    " + "\n    ".join(steps)))

        # Compile Program
        print("Compiling Program, please wait.")
        exit_code = execute_command("pyinstaller", "--noconfirm", "--onefile", "--windowed", "--icon",
                                    "assets/icons/logo.ico", outputFilename)

        if exit_code == 0:
            shutil.move(Path("dist/output.exe"), f"{PROGRAM_NAME}.exe")
            shutil.rmtree(Path("build"))
            shutil.rmtree(Path("dist"))
            print(f"Compilation was successful: {PROGRAM_NAME}.exe generated")

    os.close(outputFile)
