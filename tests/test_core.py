from datetime import datetime

import pytest

from namefile.core import FileInfo, namefile, parse


@pytest.mark.parametrize(
    'stem, suffix, tag, version, date',
    [
        ('Moka.2', 'csv', ['error', 'predicted'], None, datetime(2012, 2, 23)),
        ('Moka-1', 'csv', 'error', '1.0.1.post1', True),
        ('Moka3', 'xlse', None, '2.0.1.post1', False),
        ('company_name_match_short', 'json', None, '1.2', datetime(2012, 2, 23)),
    ],
)
def test_file_name(stem, suffix, tag, version, date):
    file_name = namefile(stem, suffix, tag, date, version)
    assert file_name.endswith(suffix)

    fileinfo1 = parse(file_name)
    if date is True:
        date = fileinfo1.date
    if date is False:
        date = None
    fileinfo2 = FileInfo(stem, suffix, tag, date, version)
    assert fileinfo1 == fileinfo2
