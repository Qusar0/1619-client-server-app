from math import ceil
from typing import Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import create_model

from src.tables.instructors.dao import InstructorDAO
from src.tables.students.dao import StudentDAO
from src.tables.groups.dao import GroupDAO
from src.tables.departments.schemas import DepartmentModel


MAX_STUDENTS_PER_GROUP = 10

class GroupBalancer:
    def __init__(self, department_id: int, session: AsyncSession):
        self.department_id = department_id
        self.session = session
        self.instructors = []
        self.students = []
        self.current_groups = []

    async def balance(self):
        await self.fetch_department_data()

        instructor_count = len(self.instructors)
        student_count = len(self.students)
        current_group_count = len(self.current_groups)

        group_count, average_students_per_group = self.calculate_group_distribution(student_count, instructor_count)

        if current_group_count == 0 and average_students_per_group != 0:
            await self.create_missing_groups(group_count)
        elif current_group_count > group_count:
            await self.remove_extra_groups(group_count)
        elif current_group_count < group_count:
            await self.create_missing_groups(group_count)

        updated_groups = await GroupDAO.find_all(session=self.session, filters=DepartmentModel(department_id=self.department_id))
        if not updated_groups:
            return

        await self.assign_instructors_to_groups(updated_groups)
        await self.assign_students_to_groups(updated_groups, average_students_per_group)

        await self.session.commit()
        return len(self.instructors)

    async def fetch_department_data(self):
        department = DepartmentModel(department_id=self.department_id)
        self.instructors = await InstructorDAO.find_all(session=self.session, filters=department)
        self.students = await StudentDAO.students_by_department_id(department_id=self.department_id, session=self.session)
        self.current_groups = await GroupDAO.find_all(session=self.session, filters=department)

    @staticmethod
    def calculate_group_distribution(student_count: int, instructor_count: int) -> Tuple[int, int]:
        if student_count <= 0 or instructor_count <= 0:
            return 0, 0

        student_in_group = ceil(student_count / MAX_STUDENTS_PER_GROUP)
        min_student_instructor = min(student_count, instructor_count)

        group_count = max(student_in_group, min_student_instructor)
        average_students_per_group = ceil(student_count / group_count) if group_count else 0

        return group_count, average_students_per_group

    async def create_missing_groups(self, group_count: int):
        current_group_count = len(self.current_groups)
        for _ in range(group_count - current_group_count):
            await GroupDAO.add_group(department_id=self.department_id, session=self.session)

    async def remove_extra_groups(self, group_count: int):
        extra_groups = self.current_groups[group_count:]
        remaining_groups = self.current_groups[:group_count]

        for extra_group in extra_groups:
            GroupModel = create_model('GroupModel', group_id=(int, ...))
            group = GroupModel(group_id=extra_group.id)
            extra_group_students = await StudentDAO.find_all(session=self.session, filters=group)

            for student in extra_group_students:
                new_group = remaining_groups[student.id % len(remaining_groups)]
                student.group_id = new_group.id

            await GroupDAO.delete_one_by_id(extra_group.id, session=self.session)

    async def assign_instructors_to_groups(self, updated_groups: List):
        for idx, group in enumerate(updated_groups):
            instructor = self.instructors[idx % len(self.instructors)]
            group.instructor_id = instructor.id

    async def assign_students_to_groups(self, updated_groups: List, average_students_per_group: int):
        student_batches = [
            self.students[i:i + average_students_per_group]
            for i in range(0, len(self.students), average_students_per_group if average_students_per_group else 1)
        ]

        assert len(student_batches) <= len(updated_groups), "Неверное распределение групп и студентов"

        for group, student_batch in zip(updated_groups, student_batches):
            for student in student_batch:
                student.group_id = group.id