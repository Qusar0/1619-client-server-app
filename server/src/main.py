from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from src.tables.instructors.router import router as instructor_router


app = FastAPI()

@app.get('/')
async def root(request: Request):
    return RedirectResponse(f'{request.url}docs')


app.include_router(instructor_router)