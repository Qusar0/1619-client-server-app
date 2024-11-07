# server

## Project Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Compile and Hot-Reload for Development

```sh
uvicorn src.main:app --reload
```