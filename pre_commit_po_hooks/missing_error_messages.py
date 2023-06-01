"""Checks for missing in PO files error messages.

Returns an error code if a found an error message not included in PO file.
"""

import argparse
import itertools
import sys
import os.path

from babel.messages import Catalog
from babel.messages.pofile import read_po, write_po





class Check:
    filenames: list[str]
    quiet: bool
    po_filepath: str
    catalog = None

    def __init__(self, filenames: list[str], quiet: bool, po_filepath: str):
        self.po_filepath = po_filepath
        self.filenames = filenames
        self.quiet = quiet

    @staticmethod
    def _get_error_message(line: str) -> str:
        return line.split('=')[1].strip().replace('"', "")

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

        filenames : list
          Set of file names to check.

        po_filepath : string
          Path to .po file storing all error messages to translate.

        quiet : bool, optional
          Enabled, don't print output to stderr when an untranslated message is found.

        Returns
        -------

        int: 0 if no missed messages found, 1 otherwise.
        """
        translated_msgs = self.load_po()

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

    def load_errors(self, filename: str) -> set[str]:
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

    parser.add_argument("filenames", nargs="*", help="Filenames to check for untranslated messages")
    parser.add_argument("po-filepath", dest="po_filepath", help="Path to .po file storing all error messages to translate")
    parser.add_argument("-q", "--quiet", action="store_true", help="Supress output")

    args = parser.parse_args()

    return Check(filenames=args.filenames, quiet=args.quiet, po_filepath=args.po_filepath).execute()



if __name__ == "__main__":
    exit(main())
