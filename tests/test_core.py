from datetime import datetime

import pytest

from namefile.core import FileInfo, namefile, parse


@pytest.mark.parametrize(
    'stem, suffix, tag, version, date',
    [
        ('Moka.2', 'csv', ['error', 'predicted'], '1.2.0.post1', datetime(2012, 2, 23)),
        ('Moka-1', 'csv', 'error', '1.0.1.post1', True),
        ('Moka3', 'xlse', None, '2.0.1.post1', False),
        ('company_name_match_short', 'json', None, '1.2', datetime(2012, 2, 23)),
        ('company_name_match_short', None, None, '1.2', datetime(2012, 2, 23)),
        ('company_name_match_short', None, None, None, None),
        ('company_name_match_short', 'csv', None, None, None),
    ],
)
def test_file_name(stem, suffix, tag, version, date):
    filename = namefile(stem, suffix, tag, date, version)
    if suffix is not None:
        assert filename.endswith(suffix)

    fileinfo1 = parse(filename)
    if date is True:
        date = fileinfo1.date
    if date is False:
        date = None
    if suffix is None:
        assert fileinfo1.is_dir()
        assert not fileinfo1.is_file()
    else:
        assert fileinfo1.is_file()
        assert not fileinfo1.is_dir()
    fileinfo2 = FileInfo(stem, suffix, tag, date, version)
    assert str(fileinfo1) == filename
    assert fileinfo1 == fileinfo2
