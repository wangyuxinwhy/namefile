# namefile

## Install

```bash
pip install namefile
```

## Usage

```python
from namefile import namefile, nameparse


filename = namefile(
    stem='glue-cola',
    suffix='csv',
    tags=('classification', 'processed'),
    date=True,
    version='1.2.0.post1'
)
# filename: 'glue_cola-classification-processed.20220917.1.2.0.post1.csv'
fileinfo = nameparse(filename)
# fileinfo: FileInfo(stem='glue_cola', suffix='csv', tags={'processed', 'classification'}, date=datetime.datetime(2022, 9, 17, 0, 0), version=<Version('1.2.0.post1')>)
assert filename == fileinfo.name() == str(fileinfo)
```
