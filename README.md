## To create a package:
1. activate poetry shell
2. delete files pyproject.toml and poetry.lock
3. commit
4. agg new tag & commit tag
5. `python setup.py build`
6. `python setup.py sdist` (создаст файл pre_commit_localization_hooks-2.0.5.tar.gz)
7. `python setup.py bdist_wheel` (создаст файл pre_commit_localization_hooks-2.0.5-py3-none-any.whl)

PS: v3.0.4 was already used for test