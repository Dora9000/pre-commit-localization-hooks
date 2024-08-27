import os
import tempfile
import pytest
import pathlib


TEST_DIR = pathlib.Path(__file__).parent.resolve() / "test_data" / "tmp"

PY_FILE = pathlib.Path(__file__).parent.resolve() / "test_data" / "errors.py"

PO_FILES = {
    "en": pathlib.Path(__file__).parent.resolve() / "test_data" / "en.po",
    "ru": pathlib.Path(__file__).parent.resolve() / "test_data" / "ru.po"
}


PO_HEADER = """
msgid ""
msgstr ""
"Project-Id-Version: PACKAGE VERSION\\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\\n"
"POT-Creation-Date: 2023-04-03 11:19+0000\\n"
"PO-Revision-Date: 2023-05-23 10:04+0000\\n"
"Last-Translator: Anonymous <noreply@weblate.org>\\n"
"Language: {0}\\n"
"Language-Team: English <http://translations.fxbet.io/projects/gambling-sass/backend/en/>\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Generated-By: Babel 2.12.1\\n"

"""


@pytest.fixture
def create_po_file(request, faker):
    def create(
        is_from_file: bool = False,
        language: str = "en",
        contents: list[(str, str)] | None = None,
        file_dir: pathlib.Path = TEST_DIR,
    ):
        if is_from_file:
            assert language in PO_FILES and os.path.isfile(PO_FILES[language])

            with open(PO_FILES[language]) as f:
                content = f.read()
        else:
            if not contents:
                contents = [(faker.pystr(min_chars=1, max_chars=100), faker.pystr(min_chars=1, max_chars=100)) for _ in range(2)]

            contents = "\n\n".join([f'msgid "{msgid}"\nmsgstr "{msgstr}"' for msgid, msgstr in contents])
            content = PO_HEADER.format(language) + contents

        f = tempfile.NamedTemporaryFile(delete=False, mode="w", dir=file_dir, suffix=".po")
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
    def create(is_from_file: bool = False, contents: list[str] | None = None, file_dir: pathlib.Path = TEST_DIR):
        if is_from_file:
            assert os.path.isfile(PY_FILE)

            with open(PY_FILE) as f:
                content = f.read()
        else:
            if not contents:
                contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(2)]

            contents = "\n    ".join([f'var_{i} = "{c}"' for i, c in enumerate(contents, start=1)])
            content = """\nclass ErrorsEnum:\n    """ + contents

        f = tempfile.NamedTemporaryFile(delete=False, mode="w", dir=file_dir, suffix=".py")

        f.write(content)
        f.seek(0)

        def teardown():
            f.close()
            os.unlink(f.name)

        request.addfinalizer(teardown)
        return f

    yield create
