from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse


app = FastAPI()


@app.get('/')
async def root(request: Request):
    return RedirectResponse(f'{request.url}docs')
