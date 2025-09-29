# ✅ Fix: Strip ANSI escape sequences, with input safety
import re

def clean_output(output):
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="ignore")
    elif not isinstance(output, str):
        output = str(output)

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', output)