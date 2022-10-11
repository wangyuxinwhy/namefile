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
    """Sanitize stem by replacing invalid characters with underscores.

    invalid characters are: ``.`` ``-`` ``/`` and ``<space>``

    Args:
        stem(str): Stem to sanitize.

    Returns:
        str: Sanitized stem.

    Example:
        .. testsetup::

            from namefile.core import sanitize_stem

        .. doctest::

            >>> sanitize_stem('foo/bar')
            'foo_bar'
            >>> sanitize_stem('foo-bar')
            'foo_bar'
    """
    for char in INVALID_STEM_CHAR:
        stem = stem.replace(char, '_')
    if not stem:
        raise ValueError('stem is empty')
    return stem


@dataclass(repr=True)
class FileInfo:
    """FileInfo ValueObj

    we use this class to represent file meta info, such as stem, tags, date, version and suffix,
    and we can call :meth:`name` to generate file name by this meta info.

    Example:
        .. testsetup:: FileInfo

            import datetime

            from packaging.version import Version

            from namefile.core import FileInfo, namefile, nameparse

        .. doctest:: FileInfo

            >>> fileinfo = FileInfo('foo', 'txt', ['bar', 'baz'], datetime.date(2020, 1, 1), Version('1.0.0'))
            >>> str(fileinfo)
            'foo-bar-baz.20200101.1.0.0.txt'

    Args:
        stem(str): Stem of file, in :meth:`__post_init__`, it will be sanitized by :func:`sanitize_stem`.
        suffix(str | None): Suffix of file.
        tags(list[str]): Tags of file, in :meth:`__post_init__`, tags will be deduplicated and sorted.
        date(datetime.date | None): Date of file.
        version(packaging.version.Version | None): Version of file.

    .. warning::

        * :attr:`stem` must not be empty.
        * :attr:`suffix` must be a valid suffix, which means it must be a string ends with a letter.
    """

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
        """Generate file name by this file info.

        generate file name by :attr:`stem`, :attr:`tags`, :attr:`date`, :attr:`version` and :attr:`suffix`.
        :meth:`__str__` is an alias of this method.

        .. note::

            * if :attr:`suffix` is None, it will return a directory name, otherwise it will return a file name.
            * if :attr:`date` is not None, it will be formatted as ``%Y%m%d`` and add to file name.
            * if :attr:`version` is not None, it will be formatted as ``str`` and add to file name.
            * if :attr:`tags` is not empty, it will be joined by ``-`` and add to file name.

        .. note::

            this method **encode** all file meta info to a file name, and :meth:`parse` is the **decode** method.

            ``FileInfo`` -(:meth:`name`)-> file name -(:meth:`parse`)-> ``FileInfo``

        Example:
            .. doctest:: FileInfo

                >>> fileinfo = FileInfo('foo', 'txt', ['bar', 'baz'], datetime.date(2020, 1, 1), Version('1.0.0'))
                >>> fileinfo.name()
                'foo-bar-baz.20200101.1.0.0.txt'
                >>> fileinfo.name() == str(fileinfo)
                True
        """
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
        """Parse file name to :class:`FileInfo`.

        Example:
            .. doctest:: FileInfo

                >>> fileinfo = FileInfo.parse('foo-bar-baz.20200101.1.0.0.txt')
                >>> fileinfo.stem
                'foo'
                >>> fileinfo.tags
                ['bar', 'baz']

        Args:
            file_name(str): File name to parse.

        Returns:
            :class:`FileInfo`: Parsed file info.
        """
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
    """Helper function to generate file name by :class:`FileInfo`.

    args are same as :class:`FileInfo`.

    Example:
        .. doctest:: FileInfo

            >>> fileinfo = namefile('foo', 'txt', ['bar', 'baz'], datetime.date(2020, 1, 1), Version('1.0.0'))
            >>> str(fileinfo)
            'foo-bar-baz.20200101.1.0.0.txt'
    """

    file_info = FileInfo(stem, suffix, tags, date, version)   # type: ignore
    return file_info.name()


def nameparse(file_name: str) -> FileInfo:
    """Helper function to parse file name to :class:`FileInfo`.

    Example:
        .. doctest:: FileInfo

            >>> fileinfo = nameparse('foo-bar-baz.20200101.1.0.0.txt')
            >>> fileinfo.stem
            'foo'
            >>> fileinfo.tags
            ['bar', 'baz']
    """
    return FileInfo.parse(file_name)
