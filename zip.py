"""
Zip up this project (no enclosing folder), excluding .git, .venv, env,
project.zip, and any .DS_Store files.
"""
import os
import zipfile

# Files or folders to skip entirely
EXCLUDES = {'.git', '.venv', 'env', 'project.zip'}
# Project-root name for the output archive
OUTPUT = 'project.zip'


def should_exclude(path: str) -> bool:
    """ Exclusions"""
    parts = path.split(os.sep)
    # skip any path containing an excluded folder
    if any(p in EXCLUDES for p in parts):
        return True
    # skip macOS DS_Store files
    if path.endswith('.DS_Store'):
        return True
    return False


def main() -> None:
    """ runs zip"""
    # remove old archive if it exists
    try:
        os.remove(OUTPUT)
    except OSError:
        pass

    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('.'):
            # prune dirs in-place so we never descend into .git/.venv/etc.
            dirs[:] = [d for d in dirs if d not in EXCLUDES]
            for fname in files:
                full = os.path.join(root, fname)
                if should_exclude(full):
                    continue
                # store relative path so no leading "./"
                arc = os.path.relpath(full, '.')
                zf.write(full, arc)


if __name__ == '__main__':
    main()
