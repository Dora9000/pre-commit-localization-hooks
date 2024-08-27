import contextlib
import io
from time import sleep

import pytest

from pre_commit_po_hooks.missing_error_messages import Check

from tests.conftest import TEST_DIR, SKIP_TESTS


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test_single_error_file_0(create_po_file, create_errors_file, faker):
    en_contents = [(faker.pystr(min_chars=1, max_chars=10), faker.pystr(min_chars=1, max_chars=10)) for _ in range(3)]
    fr_contents = en_contents + [(faker.pystr(min_chars=1, max_chars=10), faker.pystr(min_chars=1, max_chars=10))]

    py_contents = [c for c, _ in en_contents] + [faker.pystr(min_chars=1, max_chars=10) for _ in range(2)]

    en_po = create_po_file(language="en", contents=en_contents)
    fr_po = create_po_file(language="fr", contents=fr_contents)

    errors_file = create_errors_file(contents=py_contents)

    output = Check(repo_directory=str(TEST_DIR), quiet=False, po_dir=str(TEST_DIR), errors_patterns=["*.py"]).execute()

    sleep(1000)
    assert output == 0


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test_several_error_files_0(create_po_file, create_errors_file, faker):
    content_1, content_2 = [[faker.pystr(min_chars=1, max_chars=100) for _ in range(10)] for _ in range(2)]

    po_file = create_po_file(content_1 + content_2)

    errors_file_1 = create_errors_file(content_1)
    errors_file_2 = create_errors_file(content_2)

    output = Check(filenames=[errors_file_1.name, errors_file_2.name], quiet=False, po_filepath=po_file.name).execute()
    assert output == 0


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
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


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test_one_error_file_error_not_exists_1(faker, create_po_file):
    po_file = create_po_file()
    errors_file_name = faker.file_name(extension="py")

    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        output = Check(filenames=[errors_file_name], quiet=False, po_filepath=po_file.name).execute()
        assert output == 1

    err_text = stderr.getvalue()
    assert err_text == f'File {errors_file_name} was not found.\n'


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test_one_error_po_file_not_exists_1(faker, create_errors_file):
    po_file_name = faker.file_name(extension="po")
    errors_file = create_errors_file()

    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        output = Check(filenames=[errors_file.name], quiet=False, po_filepath=po_file_name).execute()
        assert output == 1

    err_text = stderr.getvalue()
    assert err_text == 'File .po was not found.\n'
