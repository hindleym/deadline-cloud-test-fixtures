# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import json
import re
from pathlib import Path

# For distributed open source and proprietary code, we must include a copyright header in source every file:
_copyright_header_re = re.compile(
    r"Copyright Amazon\.com, Inc\. or its affiliates\. All Rights Reserved\.", re.IGNORECASE
)
_generated_by_scm = re.compile(r"# file generated by setuptools_scm", re.IGNORECASE)


class CopyrightHeaderNotFoundException(Exception):
    def __init__(self, filepath: Path, *args, **kwargs) -> None:
        super().__init__(
            f"Could not find a valid Amazon.com copyright header in the top of {filepath}."
            " Please add one."
        )
        self.filepath = filepath


def _check_file(filename: Path) -> None:
    with open(filename) as infile:
        lines_read = 0
        for line in infile:
            if _copyright_header_re.search(line):
                return  # success
            lines_read += 1
            if lines_read > 10:
                raise CopyrightHeaderNotFoundException(filename)
        else:
            # __init__.py files are usually empty, this is to catch that.
            raise CopyrightHeaderNotFoundException(filename)


def _is_version_file(filename: Path) -> bool:
    if filename.name != "_version.py":
        return False
    with open(filename) as infile:
        lines_read = 0
        for line in infile:
            if _generated_by_scm.search(line):
                return True
            lines_read += 1
            if lines_read > 10:
                break
    return False


def test_copyright_headers():
    """Verifies every .py file has an Amazon copyright header."""
    root_project_dir = Path(__file__)
    # The root of the project is the directory that contains the test directory.
    while not (root_project_dir / "test").exists():
        root_project_dir = root_project_dir.parent
    # Choose only a few top level directories to test.
    # That way we don't snag any virtual envs a developer might create, at the risk of missing
    # some top level .py files.
    top_level_dirs = ["src", "test", "scripts"]
    file_count = 0
    error_files = []
    for top_level_dir in top_level_dirs:
        for glob_pattern in ("**/*.py", "**/*.sh"):
            for path in Path(root_project_dir / top_level_dir).glob(glob_pattern):
                print(path)
                if not _is_version_file(path):
                    try:
                        _check_file(path)
                    except CopyrightHeaderNotFoundException as e:
                        error_files.append(e.filepath)
                file_count += 1

    print(f"test_copyright_headers checked {file_count} files successfully.")
    assert (
        len(error_files) == 0
    ), f"Copyright headers are missing from files: {json.dumps([str(ef) for ef in error_files])}"


if __name__ == "__main__":
    test_copyright_headers()
