from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, TypeVar, Union

T = TypeVar('T')
_date_format = '%Y%m%d'
_steam_pattern = r'(?P<stem>\w+)'
_tag_pattern = r'(-(?P<tags>[\w-]+))?'
_date_pattern = r'(\.(?P<date>\d{14}))?'
_version_pattern = r'(\.(?P<version>v[\w\.]+))?'
_suffix_pattern = r'\.(?P<suffix>\w+)'
_invalid_stem_char = set('.- ')
FileNamePattern = re.compile(_steam_pattern + _tag_pattern + _date_pattern + _version_pattern + _suffix_pattern)


@dataclass
class FileInfo:
    stem: str
    suffix: str
    tags: list[str] = field(default_factory=list)
    date: Optional[datetime] = None
    version: Optional[str] = None

    def __post_init__(self):
        self._check_stem(self.stem)
        if self.suffix.startswith('.'):
            raise ValueError('no')
        self.tags = sorted(self.tags)
        if self.date is True:
            self.date = datetime.now()

    def name(self):
        suffix_string = '.' + self.suffix

        if self.tags:
            tags_string = '-' + '-'.join(self.tags)
        else:
            tags_string = ''

        if self.version is None:
            version_string = ''
        else:
            if not self.version.startswith('v'):
                version_string = 'v' + self.version
            else:
                version_string = self.version
            version_string = '.' + version_string

        if self.date is not None :
            date_string = '.' + self.date.strftime(_date_format)
        else:
            date_string = ''

        return f'{self.stem}{tags_string}{date_string}{version_string}{suffix_string}'

    @classmethod
    def parse(cls, file_name: str) -> FileInfo:
        match = re.match(FileNamePattern, file_name)
        if match is None:
            raise ValueError(f'Invalid file name: {file_name}')
        match_dict: dict[str, Any] = match.groupdict()

        if (tag := match_dict['tags']) is not None:
            match_dict['tags'] = tag.split('-')
        else:
            match_dict['tags'] = []

        if (date := match_dict['date']) is not None:
            match_dict['date'] = datetime.strptime(date, _date_format)

        file_info = cls(**match_dict)
        return file_info

    @staticmethod
    def _check_stem(stem: str) -> None:
        for c in stem:
            if c in _invalid_stem_char:
                raise ValueError(f'Invalid stem: {stem}, contains invalid character -> {c}')
