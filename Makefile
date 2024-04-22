dev: pyproject.toml
	uv pip compile pyproject.toml --extra dev | uv pip sync -
	uv pip install -e .
