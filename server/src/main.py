from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from src.tables.instructors.router import router as instructor_router
from src.tables.students.router import router as student_router
from src.tables.students_subjects.router import router as student_subjects_router


app = FastAPI()

@app.get('/')
async def root(request: Request):
    return RedirectResponse(f'{request.url}docs')


app.include_router(instructor_router)
app.include_router(student_router)
app.include_router(student_subjects_router)