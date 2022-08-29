from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Sequence, TypeVar, Union

from packaging.version import LegacyVersion, Version
from packaging.version import parse as version_parse

T = TypeVar('T')
_date_format = '%Y%m%d'
_steam_pattern = r'(?P<stem>\w+)'
_tag_pattern = r'(-(?P<tags>[\w-]+))?'
_date_pattern = r'(\.(?P<date>\d{8}))?'
_file_version_pattern = r'(\.(?P<version>[\w\.]+)-v)?'
_dir_version_pattern = r'(\.(?P<version>[\w\.]+))?'
_suffix_pattern = r'\.(?P<suffix>[a-z]+)'
_invalid_stem_char = set('.- /')
FileNamePattern = re.compile(_steam_pattern + _tag_pattern + _date_pattern + _file_version_pattern + _suffix_pattern)
DirNamePattern = re.compile(_steam_pattern + _tag_pattern + _date_pattern + _dir_version_pattern)


def sanitize_string(stem: str) -> str:
    for c in _invalid_stem_char:
        stem = stem.replace(c, '_')
    return stem


class VersionType(str, Enum):
    major: int
    minor: int
    micro: int


@dataclass(repr=True)
class FileInfo:
    stem: str
    suffix: Optional[str] = None
    tags: set[str] = field(default_factory=set)
    date: Optional[datetime] = None
    version: Optional[Version] = None

    def __post_init__(self):
        self.stem = sanitize_string(self.stem)
        if self.tags is None:
            self.tags = set()
        elif isinstance(self.tags, str):
            self.tags = set([self.tags])
        self.tags = set([sanitize_string(tag) for tag in self.tags])

        if isinstance(self.version, str):
            version = version_parse(self.version)
            if isinstance(version, LegacyVersion):
                raise ValueError('LegacyVersion is not supported')
            self.version = version

    def __str__(self) -> str:
        return self.name()

    def name(self) -> str:
        if self.suffix is None:
            suffix = ''
        else:
            suffix = '.' + self.suffix

        if self.tags:
            tags = '-' + '-'.join(sorted(list(self.tags)))
        else:
            tags = ''

        if self.version is None:
            version = ''
        else:
            if self.is_file():
                version = '.' + str(self.version) + '-v'
            else:
                version = '.' + str(self.version)

        if self.date is not None:
            date = '.' + self.date.strftime(_date_format)
        else:
            date = ''

        return f'{self.stem}{tags}{date}{version}{suffix}'

    @classmethod
    def parse(cls, file_name: str) -> FileInfo:
        match = re.match(FileNamePattern, file_name) or re.match(DirNamePattern, file_name)
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

    def is_file(self):
        return self.suffix is not None

    def is_dir(self):
        return self.suffix is None


def namefile(
    stem: str,
    suffix: Optional[str] = None,
    tags: Optional[Union[str, Sequence[str]]] = None,
    date: Optional[Union[bool, datetime]] = False,
    version: Optional[str] = None,
) -> str:
    if isinstance(tags, str):
        tags = [tags]
    elif tags is None:
        tags = []

    if date is True:
        date = datetime.now()
    elif date is False:
        date = None

    _version = version_parse(version) if version is not None else None
    if isinstance(_version, LegacyVersion):
        raise ValueError('LegacyVersion is not supported')

    _suffix = suffix or None
    file_info = FileInfo(stem, _suffix, set(tags), date, _version)
    return file_info.name()


def parse(file_name: str) -> FileInfo:
    return FileInfo.parse(file_name)
