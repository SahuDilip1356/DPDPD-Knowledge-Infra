"""Write files into one gitignored folder without ever writing through a planted link.

Used by scripts that write market-lane or draft data. `write_files(repo, rel, files)`:
- refuses any name that is not a plain file name;
- refuses the folder unless git ignores it;
- walks to the folder one part at a time from the repo root, refusing any part that is a
  symlink (O_NOFOLLOW on each step), and creates missing parts only on that verified walk;
- writes each file to a new temp name created with O_EXCL inside the verified folder, then
  renames it over the target. A rename replaces the folder entry, so an existing symlink or
  hard link at the target name is replaced, never written through;
- prepares nothing until every name is checked, so a bad name means nothing is written.

If the folder is swapped for a symlink after the walk, the rename looks for the temp file in
the new place, does not find it, and fails: the write fails closed.
"""

import os
import re
import secrets
import subprocess
import sys

PLAIN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,200}$")


def _fail(msg):
    sys.exit(f"Refusing to write: {msg}")


def _ignored(repo, path):
    try:
        res = subprocess.run(["git", "-C", repo, "check-ignore", "-q", path])
    except FileNotFoundError:
        _fail("git is not available to confirm the folder is gitignored.")
    return res.returncode == 0


def _open_folder(repo, rel):
    fd = os.open(repo, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in rel:
            if not PLAIN_NAME.match(part):
                _fail(f"folder part {part!r} is not a plain name.")
            try:
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(part, 0o755, dir_fd=fd)
                nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except OSError:
                _fail(f"folder part {part!r} is a symlink or not a folder.")
            os.close(fd)
            fd = nxt
        return fd
    except BaseException:
        os.close(fd)
        raise


def write_files(repo, rel, files):
    """files: {name: text}. Writes every file into repo/<rel...>/ or exits without writing."""
    repo = os.path.realpath(repo)
    for name in files:
        if not isinstance(name, str) or not PLAIN_NAME.match(name):
            _fail(f"{name!r} is not a plain file name.")
    folder = os.path.join(repo, *rel)
    if not _ignored(repo, os.path.join(folder, "x")):
        _fail(f"{folder} is not gitignored.")
    dfd = _open_folder(repo, rel)
    written = []
    try:
        for name, text in files.items():
            tmp = f".tmp-{secrets.token_hex(8)}-{name}"
            fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644, dir_fd=dfd)
            with os.fdopen(fd, "w", newline="") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(os.path.join(folder, tmp), os.path.join(folder, name))
            written.append(os.path.join(folder, name))
    finally:
        os.close(dfd)
    return written
