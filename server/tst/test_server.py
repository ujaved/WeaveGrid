import pytest
import server
from pathlib import Path
from getpass import getuser
from random import random

FILESYSTEM = 'test_filesystem'
SUBDIR_1 = 'subdir1'
SUBDIR_EMPTY = 'subdir_empty'
FILE_1 = 'file1'
FILE_1_CONTENTS = 'WeaveGrid\n'

# create an empty test filesystem in the current directory
@pytest.fixture
def empty_filesystem():
    filesystem = Path(Path.cwd(), FILESYSTEM)
    filesystem.mkdir()

    yield filesystem

    # teardown
    filesystem.rmdir()

@pytest.fixture
def filesystem_with_one_file(empty_filesystem):
    file1 = Path(empty_filesystem, FILE_1)
    file1.write_text(FILE_1_CONTENTS)

    yield (empty_filesystem, file1)

    # teardown
    file1.unlink()

@pytest.fixture
def normal_filesystem(filesystem_with_one_file):
    base_dir = filesystem_with_one_file[0]
    subdir1 = Path(base_dir, SUBDIR_1)
    subdir1.mkdir()

    subdir_empty = Path(base_dir, SUBDIR_1, SUBDIR_EMPTY)
    subdir_empty.mkdir()

    file_symlink = Path(base_dir, SUBDIR_1, FILE_1)
    file_symlink.symlink_to(filesystem_with_one_file[1])

    yield (base_dir, subdir1, subdir_empty, file_symlink)

    # teardown
    subdir_empty.rmdir()
    file_symlink.unlink()
    subdir1.rmdir()


def entry_is_valid(entry, name, path, owner, is_dir, size):
    return (entry['name'] == name) and (entry['path'] == path) and (entry['owner'] == owner) and (entry['is_dir'] is is_dir) and (entry['size (bytes)'] == size)  

def test_invalid_file():
    p = Path(str(random()))
    assert server.getContents(p) == server.ERR_MSG.format(p)

def test_empty_filesystem(empty_filesystem):
    assert len(server.getContents(empty_filesystem)) == 0

def test_filesystem_with_one_file(filesystem_with_one_file):
    base_dir = filesystem_with_one_file[0]
    file = filesystem_with_one_file[1]
    base_dir_contents = server.getContents(base_dir)

    assert len(base_dir_contents) == 1
    assert entry_is_valid(base_dir_contents[0], FILE_1, str(file), getuser(), False, len(FILE_1_CONTENTS))
    
    assert server.getContents(file) == FILE_1_CONTENTS

def test_normal_filesystem(normal_filesystem):
    base_dir = normal_filesystem[0]
    subdir1 = normal_filesystem[1]
    subdir_empty = normal_filesystem[2]
    file = normal_filesystem[3]
    base_dir_contents = server.getContents(base_dir)
    subdir1_contents = server.getContents(subdir1)
    subdir_empty_contents = server.getContents(subdir_empty)
    file_contents = server.getContents(file)

    assert len(base_dir_contents) == 2
    subdir1_entry = base_dir_contents[0] if base_dir_contents[0]['is_dir'] else base_dir_contents[1]
    assert entry_is_valid(subdir1_entry, SUBDIR_1 , str(subdir1), getuser(), True, 128)

    assert len(subdir1_contents) == 2
    subdir_empty_entry = subdir1_contents[0]
    file_entry = subdir1_contents[1]
    if not subdir_empty_entry['is_dir']:
        subdir_empty_entry = subdir1_contents[1]
        file_entry = subdir1_contents[0]
    assert entry_is_valid(subdir_empty_entry, SUBDIR_EMPTY, str(subdir_empty), getuser(), True, 64)
    assert entry_is_valid(file_entry, FILE_1 , str(file), getuser(), False, len(FILE_1_CONTENTS))

    assert len(subdir_empty_contents) == 0

    assert file_contents == FILE_1_CONTENTS
