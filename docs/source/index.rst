.. namefile documentation master file, created by
   sphinx-quickstart on Tue Oct 11 16:13:01 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

namefile
====================================

💾 Install
----------

you can install namefile with pip:

.. code-block:: bash

   pip install namefile


👋 Usage
--------

1. generate file name from file info

.. testsetup:: *
      
      import datetime

      from packaging.version import Version
      
      from namefile import namefile, nameparse

.. testcode::
   
      name = namefile(
         stem='foo',
         suffix='txt',
         tags=['bar', 'baz'],
         date=datetime.date(2020, 1, 1),
         version=Version('1.0.0'),
      )
      print(str(name))

.. testoutput::

      foo-bar-baz.20200101.1.0.0.txt

2. restore file info from file name

.. testcode::

      info = nameparse('foo-bar-baz.20200101.1.0.0.txt')
      print(repr(info))

.. testoutput::
   
      FileInfo(stem='foo', suffix='txt', tags=['bar', 'baz'], date=datetime.date(2020, 1, 1), version=<Version('1.0.0')>)


👾 Core API
-----------

.. toctree::
   :maxdepth: 2
   :caption: Reference:

   core

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
