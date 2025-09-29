import os
import git 
import glob 
import streamlit as st
# --- Git ops ---
def is_git_repo():
    try:
        git.Repo(BASE_DIR).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False
    
def clean_git_remote_url(url):
    # Replace fancy dashes or whitespace with simple hyphen and strip spaces
    url = url.strip()
    url = url.replace('—', '-')  # en-dash to hyphen
    url = url.replace('–', '-')  # em-dash to hyphen
    # You can add more replacements if needed
    return url

def git_init_and_remote(remote_url):
    repo = git.Repo.init(BASE_DIR)
    if remote_url:
        # Clean URL (replace fancy dashes etc if needed)
        remote_url = remote_url.strip()
        try:
            origin = None
            try:
                origin = repo.remote('origin')
            except ValueError:
                pass
            if origin:
                repo.delete_remote(origin)
            repo.create_remote('origin', remote_url)
        except Exception:
            pass
    return "✅ Git initialized!"

def git_status():
    repo = git.Repo(BASE_DIR)
    return repo.git.status()

def abort_ongoing_rebase(base_dir):
    rebase_merge = os.path.join(base_dir, ".git", "rebase-merge")
    rebase_apply = os.path.join(base_dir, ".git", "rebase-apply")

    for path in [rebase_merge, rebase_apply]:
        if os.path.exists(path):
            shutil.rmtree(path)

BASE_DIR = os.getcwd()

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command failed: {cmd}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    return result.stdout.strip()


def git_commit_push(files, msg, branch, username, token):
    # Init repo if not exists
    if not os.path.exists(os.path.join(BASE_DIR, ".git")):
        repo = git.Repo.init(BASE_DIR)
        st.info("Initialized new Git repo.")
    else:
        repo = git.Repo(BASE_DIR)

    # Write .gitignore
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    with open(gitignore_path, "w") as f:
        f.write("""
# ---- Virtual Environment ----
.venv/
__pycache__/

# ---- Terraform ----
terraform/.terraform/
*.tfstate
*.tfstate.backup
crash.log

# ---- Python ----
__pycache__/
*.pyc

# ---- Secrets ----
.env

# ---- Editor ----
.vscode/
.idea/

# ---- OS files ----
.DS_Store
Thumbs.db
""".strip())
    repo.git.add(".gitignore")

    # Add files recursively or specific files
    if not files or "ALL" in files:
        repo.git.add(A=True)
    else:
        repo.git.add(files)

    repo.index.commit(msg)

    # Ensure origin remote exists
    try:
        origin = repo.remote('origin')
    except ValueError:
        remote_url = st.text_input("Enter remote URL for origin (required for push):")
        if not remote_url:
            raise Exception("Remote URL required to create 'origin'.")
        origin = repo.create_remote('origin', remote_url.strip())

    # Add credentials to remote URL
    remote_url = origin.url.strip().replace('—', '-').replace('–', '-')
    if remote_url.startswith("https://"):
        protocol_removed = remote_url[8:]
        if "@" in protocol_removed:
            protocol_removed = protocol_removed.split("@", 1)[-1]
        auth_url = f"https://{username}:{token}@{protocol_removed}"
        origin.set_url(auth_url)

    # Handle ongoing rebase (auto continue with commit --no-edit)
    rebase_merge_dir = os.path.join(BASE_DIR, ".git", "rebase-merge")
    rebase_apply_dir = os.path.join(BASE_DIR, ".git", "rebase-apply")

    if os.path.exists(rebase_merge_dir) or os.path.exists(rebase_apply_dir):
        st.warning("⚠️ Rebase in progress detected, attempting to continue rebase...")

        while os.path.exists(rebase_merge_dir) or os.path.exists(rebase_apply_dir):
            try:
                # Stage all changes (resolved conflicts)
                repo.git.add(A=True)
                # Commit with no edit message (avoid editor)
                run_cmd("git commit --no-edit", cwd=BASE_DIR)
                # Continue rebase
                run_cmd("git rebase --continue", cwd=BASE_DIR)
                st.info("Git rebase --continue executed.")
            except Exception as e:
                st.error(f"Failed to continue rebase automatically: {e}")
                raise e

        st.success("✅ Rebase finished successfully.")
        return "Rebase completed, please retry your operation."

    # Checkout branch if exists or create
    if branch in repo.heads:
        repo.git.checkout(branch)
    else:
        try:
            repo.git.checkout('-b', branch, f'origin/{branch}')
        except Exception:
            repo.git.checkout('-b', branch)

    # Pull with rebase to sync remote changes
    try:
        repo.git.pull('origin', branch, '--rebase')
    except Exception as e:
        st.warning(f"Pull with rebase failed: {e}. Trying without rebase.")
        repo.git.pull('origin', branch)

    # Push changes
    origin.push(branch)

    return f"✅ Commit, pull & push to {branch} done."
