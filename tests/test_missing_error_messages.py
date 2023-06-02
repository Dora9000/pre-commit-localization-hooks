import contextlib
import io
import os
import tempfile
import pytest

from pre_commit_po_hooks.missing_error_messages import Check


@pytest.fixture
def create_po_file(request, faker):
    def create(contents: list[str] | None = None):
        if not contents:
            contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(2)]

        content = """\n#\nmsgid ""\nmsgstr ""\n\n""" + "\n\n".join(
            [f'msgid "{c}"\nmsgstr "{c}"' for c in contents]
        )

        f = tempfile.NamedTemporaryFile(delete=False, mode="w")
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
    def create(contents: list[str] | None = None):
        if not contents:
            contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(2)]

        content = """\nclass ErrorsEnum:\n    """ + "\n    ".join(
            [f'var_{i} = "{c}"' for i, c in enumerate(contents, start=1)]
        )
        f = tempfile.NamedTemporaryFile(delete=False, mode="w")

        f.write(content)
        f.seek(0)

        def teardown():
            f.close()
            os.unlink(f.name)

        request.addfinalizer(teardown)
        return f

    yield create


@pytest.mark.skip()
def test_single_error_file_0(create_po_file, create_errors_file, faker):
    contents = [faker.pystr(min_chars=1, max_chars=100) for _ in range(10)]

    po_file = create_po_file(contents)
    errors_file = create_errors_file(contents)

    output = Check(filenames=[errors_file.name], quiet=False, po_filepath=po_file.name).execute()
    assert output == 0


@pytest.mark.skip()
def test_several_error_files_0(create_po_file, create_errors_file, faker):
    content_1, content_2 = [[faker.pystr(min_chars=1, max_chars=100) for _ in range(10)] for _ in range(2)]

    po_file = create_po_file(content_1 + content_2)

    errors_file_1 = create_errors_file(content_1)
    errors_file_2 = create_errors_file(content_2)

    output = Check(filenames=[errors_file_1.name, errors_file_2.name], quiet=False, po_filepath=po_file.name).execute()
    assert output == 0


@pytest.mark.skip()
def test_one_error_file_was_updated_1(create_po_file, create_errors_file, faker):
    content = [faker.pystr(min_chars=1, max_chars=100) for _ in range(10)]

    po_file = create_po_file(content[1:])
    errors_file = create_errors_file(content)

    # first time
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        output = Check(filenames=[errors_file.name], quiet=False, po_filepath=po_file.name).execute()
        assert output == 1

    err_text = stderr.getvalue()
    assert err_text == 'File .po was updated.\n'

    # second time
    output = Check(filenames=[errors_file.name], quiet=False, po_filepath=po_file.name).execute()
    assert output == 0


@pytest.mark.skip()
def test_one_error_file_error_not_exists_1(faker, create_po_file):
    po_file = create_po_file()
    errors_file_name = faker.file_name(extension="py")

    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        output = Check(filenames=[errors_file_name], quiet=False, po_filepath=po_file.name).execute()
        assert output == 1

    err_text = stderr.getvalue()
    assert err_text == f'File {errors_file_name} was not found.\n'


@pytest.mark.skip()
def test_one_error_po_file_not_exists_1(faker, create_errors_file):
    po_file_name = faker.file_name(extension="po")
    errors_file = create_errors_file()

    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        output = Check(filenames=[errors_file.name], quiet=False, po_filepath=po_file_name).execute()
        assert output == 1

    err_text = stderr.getvalue()
    assert err_text == 'File .po was not found.\n'
