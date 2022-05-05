# RSM
Rapid Strategic Model for the San Diego Association of Governments

## Installing

To install, activate the python or conda environment you want to use,
the cd into the repository directory and run:

```shell
python -m pip install -e .
```

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


## Developing with Docker

To build the docker container, change into the repository root and run:

```shell
docker build --tag sandag_rsm .
````

### Jupyter Notebook for Development

On the host machine, run:

```shell
docker run -v $(pwd):/home/mambauser/sandag_rsm -p 8899:8899 \
  -it sandag_rsm jupyter notebook --ip 0.0.0.0 --no-browser --allow-root \
  --port 8899 --notebook-dir=/home/mambauser
```

Then visit `http://127.0.0.1:8899/tree` in your browser.
