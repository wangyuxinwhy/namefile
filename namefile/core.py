from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from typing import Any, Iterable, TypeVar

from packaging.version import LegacyVersion, Version
from packaging.version import parse as version_parse

T = TypeVar('T')
DATE_FORMAT = '%Y%m%d'
STEM_PATTERN = r'^(?P<stem>\w+)'
VALID_TAG_PATTERN = r'\w+'
TAG_PATTERN = r'(-(?P<tags>[\w-]+))?'
DATE_PATTERN = r'(\.(?P<date>\d{8}))?'
VERSION_PATTERN = r'(\.(?P<version>[\w\.]+))?'
VALID_SUFFIX_PATTERN = r'\w*[a-zA-Z]'
SUFFIX_PATTERN = rf'\.(?P<suffix>{VALID_SUFFIX_PATTERN})$'
INVALID_STEM_CHAR = set('.- /')
FILE_NAME_PATTERN = re.compile(STEM_PATTERN + TAG_PATTERN + DATE_PATTERN + VERSION_PATTERN + SUFFIX_PATTERN)
DIR_NAME_PATTERN = re.compile(STEM_PATTERN + TAG_PATTERN + DATE_PATTERN + VERSION_PATTERN)


def sanitize_stem(stem: str) -> str:
    for char in INVALID_STEM_CHAR:
        stem = stem.replace(char, '_')
    if not stem:
        raise ValueError('stem is empty')
    return stem


@dataclass(repr=True)
class FileInfo:
    stem: str
    suffix: None | str = None
    tags: list[str] = field(default_factory=list)
    date: None | datetime.date = None
    version: None | Version = None

    @staticmethod
    def _process_stem(stem: str) -> str:
        if not stem:
            raise ValueError('stem is empty')
        stem = sanitize_stem(stem)
        if not re.fullmatch(STEM_PATTERN, stem):
            raise ValueError(f'bad stem: {stem}')
        return stem

    @staticmethod
    def _process_suffix(suffix: None | str) -> None | str:
        if suffix is None or not suffix:
            return
        elif not re.fullmatch(VALID_SUFFIX_PATTERN, suffix):
            raise ValueError(f'bad suffix: {suffix}')
        return suffix

    @staticmethod
    def _process_tags(tags: None | str | Iterable[str]) -> list[str]:
        if tags is None:
            return []

        if isinstance(tags, str):
            tags = [tags]
        tags = set([sanitize_stem(tag) for tag in tags])
        for tag in tags:
            if not re.fullmatch(VALID_TAG_PATTERN, tag):
                raise ValueError(f'bad tag: {tag}')
        tags = sorted(list(tags))
        return tags

    @staticmethod
    def _process_version(version: None | str | Version) -> None | Version:
        if version is None:
            return
        if isinstance(version, str):
            parsed_version = version_parse(version)
            if isinstance(parsed_version, LegacyVersion):
                raise ValueError('LegacyVersion is not supported')
            return parsed_version
        return version

    @staticmethod
    def _process_date(date: None | bool | datetime.date | datetime.datetime) -> datetime.date | None:
        if date is None or date is False:
            return
        elif date is True:
            return datetime.date.today()
        elif isinstance(date, datetime.datetime):
            return date.date()
        elif isinstance(date, datetime.date):
            return date
        else:
            raise ValueError(f'bad date: {date}')

    def __post_init__(self):
        self.stem = self._process_stem(self.stem)
        self.suffix = self._process_suffix(self.suffix)
        self.tags = self._process_tags(self.tags)
        self.version = self._process_version(self.version)
        self.date = self._process_date(self.date)

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
            match_dict['date'] = datetime.datetime.strptime(date, DATE_FORMAT).date()

        file_info = cls(**match_dict)
        return file_info

    def is_file(self):
        return self.suffix is not None

    def is_dir(self):
        return self.suffix is None


def namefile(
    stem: str,
    suffix: None | str = None,
    tags: None | str | Iterable[str] = None,
    date: None | bool | datetime.date | datetime.datetime = False,
    version: None | str | Version = None,
) -> str:
    file_info = FileInfo(stem, suffix, tags, date, version)   # type: ignore
    return file_info.name()


def nameparse(file_name: str) -> FileInfo:
    return FileInfo.parse(file_name)
