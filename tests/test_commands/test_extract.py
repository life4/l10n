from pathlib import Path
from textwrap import dedent
import pytest
import polib
from l10n._cli import main


@pytest.fixture
def extract(project_root: Path, source_path: Path):
    def f(source):
        source_path.write_text(dedent(source))
        code = main(['extract', '--path', str(project_root), '--lang', 'ru'])
        assert code == 0
        po_path = project_root / 'locales' / 'ru.po'
        return polib.pofile(str(po_path))
    return f


def test_extract_simple(extract):
    po_file: polib.POFile = extract("""
        from l10n import Locales
        Locales()['en'].get("hello")
    """)
    assert [e.msgid for e in po_file] == ["hello"]


def test_extract_constant(extract):
    po_file: polib.POFile = extract("""
        from typing import Final
        from l10n import Locales
        msg_id: Final = "oh hi mark"
        loc = Locales()['en']
        loc.get(msg_id)
    """)
    assert [e.msgid for e in po_file] == ["oh hi mark"]


def test_extract_comment(extract):
    po_file: polib.POFile = extract("""
        from l10n import Locales
        Locales()['en'].get("hello", comment="oh hi mark")
    """)
    assert [e.comment for e in po_file] == ["oh hi mark"]


def test_extract_plural(extract):
    po_file: polib.POFile = extract("""
        from l10n import Locales
        Locales()['en'].get("{n} bird", plural="{n} birds", n=13)
    """)
    assert [e.msgid_plural for e in po_file] == ["{n} birds"]


def test_extract_context(extract):
    po_file: polib.POFile = extract("""
        from l10n import Locales
        Locales()['en'].get("open", context="a verb")
    """)
    assert [e.msgctxt for e in po_file] == ["a verb"]
