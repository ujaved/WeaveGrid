import pytest
import server
from pathlib import Path
from getpass import getuser
from random import random

FILESYSTEM = 'test_filesystem'
SUBDIR_1 = 'subdir1'
SUBDIR_2 = 'subdir2'
SUBDIR_EMPTY = 'subdir_empty'
FILE_1 = 'file1'
FILE_1_CONTENTS = 'WeaveGrid\n'
FILE_2 = 'file2'

# create an empty test filesystem in the current directory
@pytest.fixture
def empty_filesystem():
    filesystem = Path(Path.cwd(), FILESYSTEM)
    filesystem.mkdir()

    yield filesystem

    # teardown
    try:
        filesystem.rmdir()
    except FileNotFoundError:
        pass

@pytest.fixture
def filesystem_with_one_file(empty_filesystem):
    file1 = Path(empty_filesystem, FILE_1)
    file1.write_text(FILE_1_CONTENTS)

    yield (empty_filesystem, file1)

    # teardown
    file1.unlink(missing_ok=True)

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
    file_symlink.unlink(missing_ok=True)
    try:
        subdir_empty.rmdir()
        subdir1.rmdir()
    except FileNotFoundError:
        pass


def entry_is_valid(entry, name, path, owner, is_dir, size):
    return (entry['name'] == name) and (entry['path'] == path) and (entry['owner'] == owner) and (entry['is_dir'] is is_dir) and (entry['size (bytes)'] == size)  

def test_delete_invalid_file():
    p = Path(str(random()))
    assert server.deleteContents(p) == server.ERR_MSG.format(p)
    assert not p.exists()

def test_delete_empty_dir(empty_filesystem):
    assert server.deleteContents(empty_filesystem) == server.DELETE_MSG.format(empty_filesystem)
    assert not empty_filesystem.exists()

def test_delete_file(filesystem_with_one_file):
    file = filesystem_with_one_file[1]
    assert server.deleteContents(file) == server.DELETE_MSG.format(file)
    assert not file.exists()

def test_delete_non_empty_dir(filesystem_with_one_file):
    dir = filesystem_with_one_file[0]
    assert server.deleteContents(dir) == server.DELETE_ERR_MSG.format(dir)
    assert dir.exists()

def test_rename_invalid_request():
    assert server.rename(Path(), {}) == server.RENAME_REQ_ERR_MSG

def test_rename_invalid_file():
    p = Path(str(random()))
    assert server.rename(p, {"new_name": "a"}) == server.ERR_MSG.format(p)
    assert not p.exists()

def test_rename(filesystem_with_one_file):
    file = filesystem_with_one_file[1]
    new_file = file.parent / FILE_2
    assert server.rename(file, {"new_name": FILE_2}) == server.RENAME_MSG.format(file, new_file)
    assert not file.exists()
    assert new_file.exists()
    assert new_file.read_text() == FILE_1_CONTENTS
    assert server.rename(new_file, {"new_name": FILE_1}) == server.RENAME_MSG.format(new_file, file)

    dir = filesystem_with_one_file[0]
    new_dir = dir.parent / SUBDIR_2
    assert server.rename(dir, {"new_name": SUBDIR_2}) == server.RENAME_MSG.format(dir, new_dir)
    assert not dir.exists()
    assert new_dir.exists()
    assert server.rename(new_dir, {"new_name": FILESYSTEM}) == server.RENAME_MSG.format(new_dir, dir)

def test_create_already_existing(filesystem_with_one_file):
    dir = filesystem_with_one_file[0]
    file = filesystem_with_one_file[1]
    assert server.create(dir, {"is_dir": "True"}) == server.CREATE_EXISTS_MSG.format(dir)
    assert server.create(file, {"is_dir": "True"}) == server.CREATE_EXISTS_MSG.format(file)
    assert dir.exists()
    assert file.exists()

def test_create_invalid_request():
    assert server.create(Path(), {}) == server.CREATE_REQ_ERR_MSG
    assert server.create(None, {"is_dir": "False"}) == server.CREATE_REQ_ERR_MSG

def test_create_dir_missing_parents(empty_filesystem):
    p = empty_filesystem / 'a' / 'b' / 'c'
    assert server.create(p, {"is_dir": "True"}) == server.CREATE_MSG.format(p)
    assert p.exists()
    assert p.parents[0] == (empty_filesystem / 'a' / 'b')
    assert p.parents[1] == (empty_filesystem / 'a')
    assert p.parents[2] == empty_filesystem

    for parent in p.parents:
        assert parent.exists()

    # cleanup
    p.rmdir() 
    p.parents[0].rmdir()
    p.parents[1].rmdir()

def test_create_file(normal_filesystem):
    subdir1 = normal_filesystem[1]
    p = subdir1 / 'a' / 'b' / 'c.txt'
    assert server.create(p, {"is_dir": "False", "text": FILE_1_CONTENTS}) == server.CREATE_MSG.format(p)
    assert p.read_text() == FILE_1_CONTENTS
    assert p.parents[0] == (subdir1 / 'a' / 'b')
    assert p.parents[1] == (subdir1 / 'a')
    assert p.parents[2] == subdir1

    for parent in p.parents:
        assert parent.exists()

    # cleanup
    p.unlink() 
    p.parents[0].rmdir()
    p.parents[1].rmdir()


def test_get_invalid_file():
    p = Path(str(random()))
    assert server.getContents(p) == server.ERR_MSG.format(p)

def test_get_empty_filesystem(empty_filesystem):
    assert len(server.getContents(empty_filesystem)) == 0

def test_get_filesystem_with_one_file(filesystem_with_one_file):
    base_dir = filesystem_with_one_file[0]
    file = filesystem_with_one_file[1]
    base_dir_contents = server.getContents(base_dir)

    assert len(base_dir_contents) == 1
    assert entry_is_valid(base_dir_contents[0], FILE_1, str(file), getuser(), False, len(FILE_1_CONTENTS))
    
    assert server.getContents(file) == FILE_1_CONTENTS

def test_get_normal_filesystem(normal_filesystem):
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
