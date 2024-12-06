from math import ceil
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from src.tables.instructors.dao import InstructorDAO
from src.tables.students.dao import StudentDAO
from src.tables.groups.dao import GroupDAO
from pydantic import create_model

def calculate_group_distribution(student_count: int, instructor_count: int) -> Tuple[int, int, int]:
    print(student_count, instructor_count)
    if student_count <= 0 and instructor_count <= 0:
        return 0, 0
    
    if student_count <= 0 or instructor_count <= 0:
        return 1, 1
    
    student_in_group = ceil(student_count / 10)
    min_student_instructor = min(student_count, instructor_count)

    group_count = max(student_in_group, min_student_instructor)
    average_students_per_group = ceil(student_count / group_count)

    return group_count, average_students_per_group


async def balanced_function(department_id: int, session: AsyncSession):
    DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))
    department = DepartmentModel(department_id=department_id)

    instructors = await InstructorDAO.find_all(session=session, filters=department)
    instructor_count = len(instructors)
    
    students = await StudentDAO.students_by_department_id(department_id=department_id, session=session)
    student_count = len(students)

    group_count, average_students_per_group = calculate_group_distribution(student_count, instructor_count)

    current_groups = await GroupDAO.find_all(session=session, filters=department)
    current_group_count = len(current_groups)

    if current_group_count == 0:
        await GroupDAO.add_group(department_id=department_id, session=session)
    if current_group_count > group_count:
        extra_groups = current_groups[group_count:]
        remaining_groups = current_groups[:group_count]

        for extra_group in extra_groups:
            GroupModel = create_model('GroupModel', group_id=(int, ...))
            group = GroupModel(group_id=extra_group.id)
            extra_group_students = await StudentDAO.find_all(session=session, filters=group)
            for student in extra_group_students:
                new_group = remaining_groups[student.id % group_count]
                student.group_id = new_group.id

            await GroupDAO.delete_one_by_id(extra_group.id, session=session)
    elif current_group_count < group_count:
        for _ in range(group_count - current_group_count):
            await GroupDAO.add_group(department_id=department_id, session=session)

    updated_groups = await GroupDAO.find_all(session=session, filters=department)
    if not updated_groups:
        return
    
    for idx, group in enumerate(updated_groups):
        instructor = instructors[idx % instructor_count]
        group.instructor_id = instructor.id

    student_batches = [students[i:i + average_students_per_group] for i in range(0, len(students), average_students_per_group if average_students_per_group else 1)]
    print(student_batches)
    assert len(student_batches) <= len(updated_groups), "Неверное распределение групп и студентов"

    for group, student_batch in zip(updated_groups, student_batches):
        for student in student_batch:
            student.group_id = group.id

    await session.commit()
    return instructor_count
