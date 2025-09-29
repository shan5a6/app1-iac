def contentparsing(response):
    import re, os

    # Match "filename:\n content..." blocks
    matches = re.findall(r"([^\n:]+):\n(.*?)(?=\n\S+:|$)", response, re.DOTALL)

    # Ensure terraform base directory
    TERRAFORM_DIR = os.path.join(os.getcwd(), "terraform")
    os.makedirs(TERRAFORM_DIR, exist_ok=True)

    for filename, content in matches:
        filename = filename.strip()
        content = content.strip() + "\n"

        # Build full path under terraform dir
        filepath = os.path.join(TERRAFORM_DIR, filename)

        # Ensure parent directories exist (modules, etc.)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Write file content
        with open(filepath, "w") as f:
            f.write(content)

        print(f"✅ Saved {filepath}")

    return "🎉 All Terraform files & modules generated inside ./terraform/"
