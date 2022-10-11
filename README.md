# namefile

## 💾 Install

you can install namefile with pip:

```bash
pip install namefile
```

## 👋 Usage

1. generate file name from file info

```python
from namefile import namefile

name = namefile(
    stem='foo',
    suffix='txt',
    tags=['bar', 'baz'],
    date=datetime.date(2020, 1, 1),
    version=Version('1.0.0'),
)
print(str(name))
# foo-bar-baz.20200101.1.0.0.txt
```

2. restore file info from file name

```python
from namefile import nameparse

info = nameparse('foo-bar-baz.20200101.1.0.0.txt')
print(repr(info))
# FileInfo(stem='foo', suffix='txt', tags=['bar', 'baz'], date=datetime.date(2020, 1, 1), version=<Version('1.0.0')>)
```
