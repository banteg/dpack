requirements.txt: requirements.in
	uv pip compile requirements.in -o requirements.txt

install: requirements.txt
	uv pip sync requirements.txt
	uv pip install -e .
