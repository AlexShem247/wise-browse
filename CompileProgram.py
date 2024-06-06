import base64
import re
import tempfile
import os
import subprocess
import shutil
import threading
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


def stream_output(pipe, display):
    for line in iter(pipe.readline, ''):
        display(line.strip())
    pipe.close()


def execute_command(*command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                               universal_newlines=True)

    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, print))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, print))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.returncode


def get_single_file_name(folder):
    # List all files in the folder
    files = [f for f in folder.iterdir() if f.is_file()]

    # Return the name of the single file
    return files[0].name


IF_MAIN = 'if __name__ == "__main__":'

PROGRAM_NAME = "Wise Browse"

IMG_FILES = [str(Path("assets") / "img" / f) for f in os.listdir("assets/img") if f.endswith(".png")]
SRC_FILES = [str(Path("src") / f) for f in os.listdir("src") if f.endswith(".py")]

GENERATE_OUTPUT_PY = False

if __name__ == "__main__":
    if GENERATE_OUTPUT_PY:
        outputFilename = "output.py"
    else:
        outputFileObj, outputFilename = tempfile.mkstemp()
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
        exit_code = execute_command("python",  "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
                                    "--icon", "assets/icons/logo.ico", outputFilename)

        outputFile = get_single_file_name(Path("dist"))
        finalName = PROGRAM_NAME + Path(outputFile).suffix
        shutil.move(Path("dist") / outputFile, finalName)
        shutil.rmtree(Path("build"))
        shutil.rmtree(Path("dist"))
        os.remove(Path(outputFile).stem + ".spec")

        print(f"Compilation was successful: {finalName} generated")

    if not GENERATE_OUTPUT_PY:
        os.close(outputFileObj)
