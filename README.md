# namefile

## Install

```bash
pip install namefile
```

## Usage

```python
from namefile import namefile, parse


filename = namefile(
    stem='glue-cola',
    suffix='csv',
    tags=('classification', 'processed'),
    date=True,
    version='1.2.0.post1'
)
# filename: 'glue_cola-classification-processed.20220829.1.2.0.post1-v.csv'
fileinfo = parse(filename)
# fileinfo: FileInfo(stem='glue_cola', suffix='csv', tags={'classification', 'processed'}, date=datetime.datetime(2022, 8, 29, 0, 0), version=<Version('1.2.0.post1')>)
assert filename == fileinfo.name() == str(fileinfo)
```

## Development

### conda env

```shell
conda env create
```

### poetry
```shell
poetry install
```


### Makefile

```shell
# 帮助文档
make help
# 格式化代码
make style
# 静态检查
make lint
...
```

