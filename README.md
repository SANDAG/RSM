# RSM
Rapid Strategic Model for the San Diego Association of Governments



## Code Formatting

This repo use several tools to ensure a consistent code format throughout the project:

- [Black](https://black.readthedocs.io/en/stable/) for standardized code formatting,
- [Flake8](http://flake8.pycqa.org/en/latest/) for general code quality,
- [isort](https://github.com/timothycrosley/isort) for standardized order in imports, and
- [nbstripout](https://github.com/kynan/nbstripout) to ensure notebooks are committed
  to the GitHub repository without bulky outputs included.

We highly recommend that you setup [pre-commit hooks](https://pre-commit.com/)
to automatically run all the above tools every time you make a git commit. This
can be done by running:

```shell
pre-commit install
```

from the root of the repository. You can skip the pre-commit checks
with `git commit --no-verify`.
