"""Checks for missing in PO files error messages.

Returns an error code if a found an error message not included in PO file.
"""

import argparse
import itertools
import sys
import os.path
from babel.messages import Catalog
from babel.messages.pofile import read_po, write_po

from pathlib import Path


class Check:

    quiet: bool
    po_filepath: str
    catalog = None
    repo_directory: str | None
    filenames: list[Path] = []
    errors_patterns: list[str] | None

    def __init__(
        self,
        quiet: bool,
        po_filepath: str,
        repo_directory: str | None = None,
        errors_patterns: list[str] | None = None,
    ):
        self.errors_patterns = errors_patterns
        self.po_filepath = po_filepath
        self.repo_directory = repo_directory
        self.quiet = quiet

    @staticmethod
    def _get_error_message(line: str) -> str:
        return line.split('=')[1].strip().replace('"', "")

    def get_errors_filenames(self) -> list[Path]:
        try:
            self.filenames = []
            for pattern in self.errors_patterns:
                self.filenames += [p.parent / p.name for p in Path(self.repo_directory).rglob(pattern)]
        except Exception:
            if not self.quiet:
                raise Exception("Incorrect error filename pattern.\n")

        return self.filenames

    def update_po_file(self, errors: set[str]) -> None:
        new_catalog = Catalog(
            fuzzy=self.catalog.fuzzy,
            locale=self.catalog.locale,
            domain=self.catalog.domain,
            charset=self.catalog.charset,
            project=self.catalog.project,
            version=self.catalog.version,
            creation_date=self.catalog.creation_date,
            revision_date=self.catalog.revision_date,
            language_team=self.catalog.language_team,
            header_comment=self.catalog.header_comment,
            last_translator=self.catalog.last_translator,
            copyright_holder=self.catalog.copyright_holder,
            msgid_bugs_address=self.catalog.msgid_bugs_address,
        )
        for error in errors:
            new_catalog.add(error, error)

        with open(self.po_filepath, 'wb') as outfile:
            write_po(outfile, catalog=new_catalog, width=100, sort_output=True)

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
        translated_msgs = self.load_po()
        self.filenames = self.get_errors_filenames()

        errors = set(itertools.chain.from_iterable(self.load_errors(filename=filename) for filename in self.filenames))

        if sorted(list(errors)) != sorted(list(translated_msgs)):
            self.update_po_file(errors)
            if not self.quiet:
                raise Exception("File .po was updated.\n")

        return 0

    def execute(self):
        try:
            return self._execute()
        except Exception as e:
            sys.stderr.write(str(e) or f"Hook error happened: {repr(e)}")
            return 1

    def load_po(self) -> set[str]:
        if not os.path.isfile(self.po_filepath):
            if not self.quiet:
                raise Exception("File .po was not found.\n")

        with open(self.po_filepath) as f:
            catalog = read_po(f)
            self.catalog = catalog
        return set(message.id for message in catalog if message.id)

    def load_errors(self, filename: Path) -> set[str]:
        errors = set()

        if not os.path.isfile(filename):
            if not self.quiet:
                raise Exception(f"File {filename} was not found.\n")

        with open(filename) as f:
            content_lines = f.readlines()
            for i, line in enumerate(content_lines):
                if '=' in line and (error_msg := self._get_error_message(line)):
                    errors.add(error_msg)

        return errors


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
