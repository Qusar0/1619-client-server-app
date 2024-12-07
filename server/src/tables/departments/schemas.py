from pydantic import create_model

DepartmentModel = create_model('DepartmentModel', department_id=(int, ...))
