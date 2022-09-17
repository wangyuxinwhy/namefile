from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Optional, Sequence, TypeVar, Union

from packaging.version import LegacyVersion, Version
from packaging.version import parse as version_parse

T = TypeVar('T')
DATE_FORMAT = '%Y%m%d'
STEAM_PATTERN = r'^(?P<stem>\w+)'
TAG_PATTERN = r'(-(?P<tags>[\w-]+))?'
DATE_PATTERN = r'(\.(?P<date>\d{8}))?'
VERSION_PATTERN = r'(\.(?P<version>[\w\.]+))?'
SUFFIX_PATTERN = r'\.(?P<suffix>[a-z]+)$'
INVALID_STEM_CHAR = set('.- /')
FILE_NAME_PATTERN = re.compile(STEAM_PATTERN + TAG_PATTERN + DATE_PATTERN + VERSION_PATTERN + SUFFIX_PATTERN)
DIR_NAME_PATTERN = re.compile(STEAM_PATTERN + TAG_PATTERN + DATE_PATTERN + VERSION_PATTERN)


def sanitize_stem(stem: str) -> str:
    for char in INVALID_STEM_CHAR:
        stem = stem.replace(char, '_')
    return stem


@dataclass(repr=True)
class FileInfo:
    stem: str
    suffix: Optional[str] = None
    tags: set[str] = field(default_factory=set)
    date: Optional[datetime] = None
    version: Optional[Version] = None

    def __post_init__(self):
        self.stem = sanitize_stem(self.stem)
        if self.tags is None:
            self.tags = set()
        elif isinstance(self.tags, str):
            self.tags = set([self.tags])
        self.tags = set([sanitize_stem(tag) for tag in self.tags])

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
            version = '.' + str(self.version)

        if self.date is not None:
            date = '.' + self.date.strftime(DATE_FORMAT)
        else:
            date = ''

        return f'{self.stem}{tags}{date}{version}{suffix}'

    @classmethod
    def parse(cls, file_name: str) -> FileInfo:
        match = re.match(FILE_NAME_PATTERN, file_name) or re.match(DIR_NAME_PATTERN, file_name)
        if match is None:
            raise ValueError(f'Invalid file name: {file_name}')
        match_dict: dict[str, Any] = match.groupdict()

        if (tag := match_dict['tags']) is not None:
            match_dict['tags'] = tag.split('-')
        else:
            match_dict['tags'] = []

        if (date := match_dict['date']) is not None:
            match_dict['date'] = datetime.strptime(date, DATE_FORMAT)

        file_info = cls(**match_dict)
        return file_info

    def is_file(self):
        return self.suffix is not None

    def is_dir(self):
        return self.suffix is None


def namefile(
    stem: str,
    suffix: Optional[str] = None,
    tags: Optional[Union[str, Iterable[str]]] = None,
    date: Optional[Union[bool, datetime]] = False,
    version: Optional[Union[str, Version]] = None,
) -> str:
    if isinstance(tags, str):
        tags = [tags]
    elif tags is None:
        tags = []

    if date is True:
        date = datetime.now()
    elif date is False:
        date = None

    if isinstance(version, str):
        _version = version_parse(version)
        if isinstance(_version, LegacyVersion):
            raise ValueError('LegacyVersion is not supported')
    else:
        _version = version

    file_info = FileInfo(stem, suffix, set(tags), date, _version)
    return file_info.name()


def nameparse(file_name: str) -> FileInfo:
    return FileInfo.parse(file_name)
