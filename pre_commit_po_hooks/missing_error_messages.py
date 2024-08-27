"""Checks for missing in PO files error messages.

Returns an error code if a found an error message not included in PO file.
"""

import argparse
import sys
from pathlib import Path

from pre_commit_po_hooks import utils


class Check:

    quiet: bool
    po_filepath: str
    repo_directory: str
    errors_patterns: list[str]

    _catalog = None

    def __init__(self, quiet: bool, po_filepath: str, repo_directory: str, errors_patterns: list[str]):
        self.quiet = quiet
        self.po_filepath = po_filepath
        self.repo_directory = repo_directory
        self.errors_patterns = errors_patterns

        if not self.quiet:
            sys.stdout.write(
                f"Run with args: \n"
                f"`errors_patterns`: {self.errors_patterns},\n"
                f"`repo_directory`: {self.repo_directory},\n"
                f"`po_filepath`: {self.po_filepath}\n"
            )

    def get_errors_filenames(self) -> list[Path]:
        filenames = []
        try:
            for pattern in self.errors_patterns:
                filenames += [p.parent / p.name for p in Path(self.repo_directory).rglob(pattern)]
        except Exception:
            raise Exception("Incorrect error filename pattern.\n")

        if not self.quiet:
            sys.stdout.write("Found error files: " + str(filenames) + '\n')

        return filenames


    def _execute(self):
        """Warns about all missed error messages found in filenames that not included in PO files.

        Parameters
        ----------
        errors_patterns : list[str]
          Pattern of errors.py filenames

        repo_directory : str
          Path to repository containing errors.py files

        po_filepath : string
          Path to .po file storing all error messages to translate.

        quiet : bool, optional
          Enabled, don't print output to stderr when an untranslated message is found.

        Returns
        -------

        int: 0 if no missed messages found, 1 otherwise.
        """
        po_data, self._catalog = utils.load_po(self.po_filepath)
        py_data = utils.load_py(filenames=self.get_errors_filenames())

        if sorted(list(py_data)) != sorted(list(po_data)):
            if not self.quiet:
                sys.stdout.write(f"Discrepancy found. {len(py_data)} msgs, {len(po_data)} in .po file.\n")

            utils.update_po_file(errors=py_data, catalog=self._catalog, po_filepath=self.po_filepath)
            if not self.quiet:
                raise Exception("File .po was updated.\n")

            return 1

        return 0

    def execute(self):
        try:
            return self._execute()
        except Exception as e:
            sys.stderr.write(str(e) or f"Hook error happened: {repr(e)}")
            return 1


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", nargs="*", help="Changed files")
    parser.add_argument("-q", "--quiet", required=False, default=False, help="Supress output")
    parser.add_argument("--repo_directory", required=True, help="Path to repository containing errors.py files")
    parser.add_argument("--po_filepath", required=True, help="Path to .po file storing all error messages to translate")
    parser.add_argument(
        "--errors_patterns", required=False, nargs='*', default=["errors.py"], help="Pattern of errors.py filenames"
    )

    args = parser.parse_args()

    if not args.filenames:
        return 0

    return Check(
        quiet=args.quiet,
        po_filepath=args.po_filepath,
        repo_directory=args.repo_directory,
        errors_patterns=args.errors_patterns,
    ).execute()


if __name__ == "__main__":
    exit(main())
