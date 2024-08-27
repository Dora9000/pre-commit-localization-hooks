import pytest
from pre_commit_po_hooks.missing_error_messages import Check
from tests.conftest import TEST_DIR


SKIP_TESTS = False


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test(create_po_file, create_errors_file, faker):
    en_contents = [(faker.pystr(min_chars=1, max_chars=10), faker.pystr(min_chars=1, max_chars=10)) for _ in range(3)]
    fr_contents = en_contents + [(faker.pystr(min_chars=1, max_chars=10), faker.pystr(min_chars=1, max_chars=10))]
    py_contents = [c for c, _ in en_contents] + [faker.pystr(min_chars=1, max_chars=10) for _ in range(2)]

    en_po = create_po_file(language="en", contents=en_contents)
    fr_po = create_po_file(language="fr", contents=fr_contents)
    errors_file = create_errors_file(contents=py_contents)

    output = Check(repo_directory=str(TEST_DIR), quiet=False, po_dir=str(TEST_DIR), errors_patterns=["*.py"]).execute()

    # sleep(1000)
    assert output == 1

    output = Check(repo_directory=str(TEST_DIR), quiet=False, po_dir=str(TEST_DIR), errors_patterns=["*.py"]).execute()
    assert output == 0


@pytest.mark.skipif(SKIP_TESTS, reason="no test")
def test__black(create_po_file, create_errors_file):
    en_po = create_po_file(language="en", is_from_file=True)
    errors_file = create_errors_file(is_from_file=True)

    output = Check(repo_directory=str(TEST_DIR), quiet=False, po_dir=str(TEST_DIR), errors_patterns=["*.py"]).execute()
    assert output == 1

    output = Check(repo_directory=str(TEST_DIR), quiet=False, po_dir=str(TEST_DIR), errors_patterns=["*.py"]).execute()
    assert output == 0
