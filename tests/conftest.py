import os
import tempfile

import pytest

import pathlib
a = pathlib.Path(__file__).parent.resolve()

print(a)

SKIP_TESTS = False
TEST_DIR = pathlib.Path(__file__).parent.resolve() / "test_data" / "tmp"

PO_FILE = pathlib.Path(__file__).parent.resolve() / "test_data" / "test_en.po"
PY_FILE = pathlib.Path(__file__).parent.resolve() / "test_data" / "test_errors.py"



@pytest.fixture
def create_po_file(request, faker):
    def create(from_file: bool = False, contents: list[str] | None = None):
        assert not (from_file and contents)

        if from_file:
            with open(PO_FILE) as f:
                content = f.read()
        else:
            if not contents:
                contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(2)]

            contents = "\n\n".join([f'msgid "{c}"\nmsgstr "{c}"' for c in contents])
            content = """\n#\nmsgid ""\nmsgstr ""\n\n""" + contents

        print(content)
        f = tempfile.NamedTemporaryFile(delete=False, mode="w", dir=TEST_DIR, suffix=".po")
        f.write(content)
        f.seek(0)

        def teardown():
            f.close()
            os.unlink(f.name)

        request.addfinalizer(teardown)
        return f

    yield create


@pytest.fixture
def create_errors_file(request, faker):
    def create(from_file: bool = False, contents: list[str] | None = None):
        assert not (from_file and contents)

        if from_file:
            with open(PY_FILE) as f:
                content = f.read()
        else:
            if not contents:
                contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(2)]

            contents = "\n    ".join([f'var_{i} = "{c}"' for i, c in enumerate(contents, start=1)])
            content = """\nclass ErrorsEnum:\n    """ + contents

        f = tempfile.NamedTemporaryFile(delete=False, mode="w", dir=TEST_DIR, suffix=".py")

        f.write(content)
        f.seek(0)

        def teardown():
            f.close()
            os.unlink(f.name)

        request.addfinalizer(teardown)
        return f

    yield create
