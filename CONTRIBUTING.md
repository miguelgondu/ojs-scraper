# How to contribute to this project

We assume that you have [`uv` installed](https://docs.astral.sh/uv/getting-started/installation/).

Once you install `uv`, you can sync the project with
```bash
uv sync
```

This includes, among other things, the `pre-commit` package. Install
the pre-commit hooks using
```bash
uv run pre-commit install
```

Now every time we make a commit, the hooks will run. This lints and formats
the code.
