from __future__ import annotations
import datetime
from hypothesis import given, note
from hypothesis import strategies as st
from packaging.version import parse as version_parse

from namefile.core import (
    STEM_PATTERN,
    VALID_SUFFIX_PATTERN,
    VALID_TAG_PATTERN,
    FileInfo,
    namefile,
    nameparse,
)

tag_string_strategy = st.from_regex(VALID_TAG_PATTERN, fullmatch=True)


@given(
    stem=st.from_regex(STEM_PATTERN, fullmatch=True),
    suffix=st.one_of(st.none(), st.from_regex(VALID_SUFFIX_PATTERN, fullmatch=True)),
    tags=st.one_of(st.none(), tag_string_strategy, st.lists(tag_string_strategy, min_size=1)),
    date=st.one_of(st.none(), st.booleans(), st.dates(min_value=datetime.date(2000, 1, 1)), st.datetimes(min_value=datetime.datetime(2000, 1, 1))),
    version=st.one_of(st.none(), st.just('1.0.1.post1'), st.just('2.0')),
)
def test_file_name(stem, suffix, tags, date, version):
    filename = namefile(stem, suffix, tags, date, version)
    if suffix is not None:
        assert filename.endswith(suffix)

    fileinfo1 = nameparse(filename)
    if date is True:
        date = fileinfo1.date
    if date is False:
        date = None

    if not suffix:
        assert fileinfo1.suffix is None

    else:
        assert fileinfo1.suffix == suffix

    if version is not None:
        assert fileinfo1.version == version_parse(str(version))

    fileinfo2 = FileInfo(stem, suffix, tags, date, version)   # type: ignore
    note(f'{fileinfo1!r}')
    note(f'{fileinfo2!r}')

    assert str(fileinfo1) == filename
    assert fileinfo1 == fileinfo2
