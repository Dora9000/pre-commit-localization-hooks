## To create a package:
1. activate poetry shell
2. delete files pyproject.toml and poetry.lock
3. `python setup.py build`
4. `python setup.py sdist` (создаст файл pre_commit_localization_hooks-2.0.5.tar.gz)
5. `python setup.py bdist_wheel` (создаст файл pre_commit_localization_hooks-2.0.5-py3-none-any.whl)
