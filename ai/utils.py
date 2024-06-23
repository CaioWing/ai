import subprocess
import os
import git
from pathlib import Path

def run_bash_command(command: str) -> str:
    allowed_commands = ['ls', 'cat', 'grep', 'head', 'tail', 'wc', 'diff', 'find', 'sort', 'uniq', 'cd', 'mkdir', 'for']
    command_parts = command.split()
    if command_parts[0] not in allowed_commands:
        return f"Error: Command '{command_parts[0]}' is not allowed."

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def modify_file(file_path: str, new_content: str) -> None:
    path = Path(file_path)
    # if not path.is_relative_to(Path.cwd()):
    #     raise ValueError("File path must be within the current working directory")
    # if not path.exists():
    #     raise FileNotFoundError(f"File {file_path} does not exist")
    with open(path, 'w') as file:
        file.write(new_content)

def create_branch_and_commit(repo_path: str, branch_name: str, file_path: str, commit_message: str) -> None:
    repo = git.Repo(repo_path)
    current_branch = repo.active_branch
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()

    repo.index.add([file_path])
    repo.index.commit(commit_message)

    current_branch.checkout()

def run_main_file(main_file: str) -> str:
    path = Path(main_file)
    if not path.is_relative_to(Path.cwd()):
        raise ValueError("Main file must be within the current working directory")
    if not path.exists():
        raise FileNotFoundError(f"File {main_file} does not exist")
    try:
        result = subprocess.run(['python', str(path)], check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
