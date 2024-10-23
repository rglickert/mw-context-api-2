import os
import subprocess
import shutil
import re
from pathlib import Path
import git

def is_github_url(url):
    github_pattern = r'https?://github\.com/[\w-]+/[\w-]+(?:\.git)?/?'
    return re.match(github_pattern, url) is not None

def add_context_folder(repo_url):
    context_folders_path = Path('context_folders')
    context_folders_path.mkdir(exist_ok=True)

    if is_github_url(repo_url):
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        new_folder_path = context_folders_path / repo_name
        if new_folder_path.exists():
            print(f"Updating existing repository: {repo_name}")
            repo = git.Repo(new_folder_path)
            origin = repo.remotes.origin
            origin.pull()
        else:
            print(f"Cloning new repository: {repo_name}")
            git.Repo.clone_from(repo_url, new_folder_path)
    else:
        local_path = Path(repo_url)
        new_folder_name = local_path.name
        new_folder_path = context_folders_path / new_folder_name
        if new_folder_path.exists():
            print(f"Updating existing folder: {new_folder_name}")
            shutil.rmtree(new_folder_path)
        else:
            print(f"Adding new folder: {new_folder_name}")
        new_folder_path.mkdir(parents=True, exist_ok=True)

        for file in local_path.rglob('*'):
            if file.is_file() and (file.suffix in ('.py', '.json', '.txt', '.csv') or file.name == 'extra_model_paths.yml'):
                rel_path = file.relative_to(local_path)
                dst_file = new_folder_path / rel_path
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, dst_file)

    gitignore_path = Path('.gitignore')
    gitignore_content = (
        "context_folders/*\n"
        "!context_folders/**/*.py\n"
        "!context_folders/**/*.json\n"
        "!context_folders/**/*.txt\n"
        "!context_folders/**/*.csv\n"
        "!context_folders/**/extra_model_paths.yml\n"
    )
    if not gitignore_path.exists() or gitignore_content not in gitignore_path.read_text():
        with gitignore_path.open('a') as f:
            f.write(gitignore_content)

    try:
        repo = git.Repo('.')
        repo.git.add('.')
        repo.index.commit(f"Add/Update context folder: {new_folder_path.name}")
        origin = repo.remote('origin')
        origin.push()
        print(f"Context folder {new_folder_path.name} added/updated and pushed successfully.")
    except git.GitCommandError as e:
        print(f"An error occurred while performing Git operations: {e}")

if __name__ == "__main__":
    input_path = input("Enter the GitHub URL or local path of the folder you want to add as a context folder: ").strip()
    add_context_folder(input_path)