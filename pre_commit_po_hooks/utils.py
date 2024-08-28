import ast
import os
from pathlib import Path

from babel.messages import Catalog
from babel.messages.pofile import read_po, write_po


def load_po(po_filepath: Path) -> Catalog:
    if not os.path.isfile(po_filepath):
        raise Exception("File .po was not found.\n")

    with open(po_filepath) as f:
        catalog = read_po(f)

    return catalog


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


def load_py(filenames: list[Path]) -> set[str]:
    errors = []

    for filename in filenames:
        if not os.path.isfile(filename):
            raise Exception(f"File {filename} was not found.\n")

        with open(filename) as f:
            content = f.read()

        content = ast.parse(content)

        for node in content.body:
            if isinstance(node, ast.ClassDef):
                errors.extend(enum_field.value.value for enum_field in node.body)

    if len(errors) != len(set(errors)):
        raise Exception(f"Error messages are not unique.\n")

    return set(errors)
