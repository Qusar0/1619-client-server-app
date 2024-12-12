from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from src.tables.instructors.router import router as instructor_router
from src.tables.students.router import router as student_router
from src.tables.students_subjects.router import router as student_subjects_router
from src.tables.departments.router import router as department_router
from src.tables.groups.router import router as group_router


app = FastAPI()

origins = ['http://localhost:5173']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root(request: Request):
    return RedirectResponse(f'{request.url}docs')


app.include_router(instructor_router)
app.include_router(student_router)
app.include_router(student_subjects_router)
app.include_router(department_router)
app.include_router(group_router)