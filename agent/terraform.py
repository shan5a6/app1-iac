import subprocess
from agent.llm import calling_groq
import os

def run_terraform_command(command, TERRAFORM_DIR="terraform", values_files=None):
    try:
        subprocess.run(["terraform", "init", "-input=false"], cwd=TERRAFORM_DIR, check=True, capture_output=True)

        tf_command = ["terraform", command]
        if command in ["apply", "destroy"]:
            tf_command.append("-auto-approve")

        # Add values files if provided
        if values_files:
            for vf in values_files:
                tf_command.extend(["-var-file", vf])

        result = subprocess.run(tf_command, cwd=TERRAFORM_DIR, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

def terraform_format(TERRAFORM_DIR="terraform"):
    try:
        result = subprocess.run(["terraform", "fmt"], cwd=TERRAFORM_DIR, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

def terraform_validate(TERRAFORM_DIR="terraform"):
    try:
        result = subprocess.run(["terraform", "validate"], cwd=TERRAFORM_DIR, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

def terraform_explain(TERRAFORM_DIR="terraform"):
    try:
        print("I am inside code explain")
        main_tf_path = os.path.join(TERRAFORM_DIR, "main.tf")
        if not os.path.exists(main_tf_path):
            return "❌ main.tf file not found."
        with open(main_tf_path) as f:
            code = f.read()
        prompt = f"Explain this Terraform code:\n\n{code}"
        print(prompt)
        return calling_groq(prompt)
    except Exception as e:
        return str(e)

