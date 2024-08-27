"""Checks for missing in PO files error messages.

Returns an error code if a found an error message not included in PO file.
"""

import argparse
import os
import sys
from pathlib import Path
import ast
from babel.messages import Catalog
from babel.messages.pofile import read_po, write_po


class Check:

    quiet: bool
    po_dir: str
    repo_directory: str
    errors_patterns: list[str]

    def __init__(self, quiet: bool, po_dir: str, repo_directory: str, errors_patterns: list[str]):
        self.quiet = quiet
        self.po_dir = po_dir
        self.repo_directory = repo_directory
        self.errors_patterns = errors_patterns

        if not self.quiet:
            sys.stdout.write(
                f"Run with args: \n"
                f"`errors_patterns`: {self.errors_patterns},\n"
                f"`repo_directory`: {self.repo_directory},\n"
                f"`po_dir`: {self.po_dir}\n"
            )

    @staticmethod
    def load_po(po_filepath: Path) -> Catalog:
        if not os.path.isfile(po_filepath):
            raise Exception("File .po was not found.\n")

        with open(po_filepath) as f:
            catalog = read_po(f)

        return catalog

    @staticmethod
    def update_po_file(errors: set[(str, str)], catalog: Catalog, po_filepath: Path) -> None:
        new_catalog = Catalog(
            fuzzy=catalog.fuzzy,
            locale=catalog.locale,
            domain=catalog.domain,
            charset=catalog.charset,
            project=catalog.project,
            version=catalog.version,
            creation_date=catalog.creation_date,
            revision_date=catalog.revision_date,
            language_team=catalog.language_team,
            header_comment=catalog.header_comment,
            last_translator=catalog.last_translator,
            copyright_holder=catalog.copyright_holder,
            msgid_bugs_address=catalog.msgid_bugs_address,
        )
        for msgid, msgstr in errors:
            new_catalog.add(msgid, msgstr)

        with open(po_filepath, 'wb') as outfile:
            write_po(outfile, catalog=new_catalog, width=100, sort_output=True)

    @staticmethod
    def load_py(filenames: list[Path]) -> set[str]:
        errors = set()

        for filename in filenames:
            if not os.path.isfile(filename):
                raise Exception(f"File {filename} was not found.\n")

            with open(filename) as f:
                content = f.read()

            content = ast.parse(content)

            for node in content.body:
                if isinstance(node, ast.ClassDef):
                    errors |= set(enum_field.value.value for enum_field in node.body)

        return errors

    def get_py_filenames(self) -> list[Path]:
        filenames = []
        try:
            for pattern in self.errors_patterns:
                filenames += [
                    p for p in Path(self.repo_directory).rglob(pattern)
                    if not any(x.startswith('.') or x.startswith('_') for x in p.parts)
                ]
        except Exception:
            raise Exception("Incorrect error filename pattern.\n")

        if not self.quiet:
            sys.stdout.write("Found error files: " + str(filenames) + '\n')

        return filenames

    def get_po_filenames(self, po_dir: str) -> list[Path]:
        return [p.parent / p.name for p in Path(po_dir).rglob("*.po") if os.path.isfile(p.parent / p.name)]

    def update_en_po(self, poes_data: dict, py_objects: set[str]) -> int:
        (filename, catalog), *_ = [
            (filename, catalog) for filename, catalog in poes_data.items() if catalog.locale_identifier == 'en'
        ]
        po_objects = set(message.id for message in catalog if message.id)

        if sorted(list(py_objects)) != sorted(list(po_objects)):
            self.update_po_file(
                errors=set((e, e) for e in py_objects), catalog=catalog, po_filepath=Path(self.po_dir) / filename
            )
            return 1

        return 0

    def update_non_en_po(self, poes_data: dict, py_objects: set[str]) -> int:
        res = 0

        for filename, catalog in poes_data.items():
            if catalog.locale_identifier == 'en':
                continue

            messages = {message.id: message.string for message in catalog if message.id}

            if messages.keys() - py_objects:
                res = 1
                self.update_po_file(
                    catalog=catalog,
                    po_filepath=Path(self.po_dir) / filename,
                    errors=set(
                        (message_id, message_text)
                        for message_id, message_text in messages.items() if message_id in py_objects
                    ),
                )

        return res

    def _execute(self):
        """Warns about all missed error messages found in filenames that not included in PO files.

        Parameters
        ----------
        errors_patterns : list[str]
          Pattern of errors.py filenames

        repo_directory : str
          Path to repository containing errors.py files

        po_dir : string
          Path to dir with .po files.

        quiet : bool, optional
          Enabled, don't print output to stderr when an untranslated message is found.

        Returns
        -------

        int: 0 if no missed messages found, 1 otherwise.
        """
        py_objects = self.load_py(filenames=self.get_py_filenames())

        poes_data = {f.name: self.load_po(po_filepath=f) for f in self.get_po_filenames(self.po_dir)}

        res1 = self.update_en_po(poes_data, py_objects=py_objects)
        res2 = self.update_non_en_po(poes_data, py_objects=py_objects)

        if res1 and not self.quiet:
            raise Exception("File .po was updated.\n")

        if res2 and not self.quiet:
            raise Exception("Non default .po files were updated.\n")

        return min(sum([res1, res2]), 1)

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
    parser.add_argument("--po_dir", required=True, help="Path to dir with .po files")
    parser.add_argument(
        "--errors_patterns", required=False, nargs='*', default=["errors.py"], help="Pattern of errors.py filenames"
    )

    args = parser.parse_args()

    if not args.filenames:
        return 0

    return Check(
        quiet=args.quiet,
        po_dir=args.po_dir,
        repo_directory=args.repo_directory,
        errors_patterns=args.errors_patterns,
    ).execute()


if __name__ == "__main__":
    exit(main())
