<template>
  <div class="table__container">
    <table>
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              @change="toggleSelectAllInstructors"
              v-model="selectAllInstructors"
            />
          </th>
          <th>Фамилия Имя</th>
          <th>Кафедра</th>
          <th>Группы</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="instructor in instructors" :key="instructor.id">
          <td>
            <input
              type="checkbox"
              v-model="selectedInstructors"
              :value="instructor.id"
            />
          </td>
          <td>{{ instructor.first_name }} {{ instructor.last_name }}</td>
          <td>{{ instructor.department }}</td>
          <td>
            <ul>
              <li v-for="group in instructor.groups" :key="group.id">
                {{ group }}
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="table__container">
    <table>
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              @change="toggleSelectAllStudents"
              v-model="selectAllStudents"
            />
          </th>
          <th>Фамилия Имя</th>
          <th>Кафедра</th>
          <th>Группa</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.id">
          <td>
            <input
              type="checkbox"
              v-model="selectAllStudents"
              :value="student.id"
            />
          </td>
          <td>{{ student.first_name }} {{ student.last_name }}</td>
          <td>{{ student.department }}</td>
          <td>{{ student.group }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import api from "@/services/api";
import { computed, onMounted, ref } from "vue";

let instructors = ref([]);
let selectedInstructors = ref([]);
let selectAllInstructors = ref(false);

let students = ref([]);
let selectedStudents = ref([]);
let selectAllStudents = ref(false);

const getInstructors = async () => {
  try {
    const responce = await api.get("/instructors/");
    instructors.value = responce.data;
  } catch (error) {
    console.error("Ошибка при получении кураторов:", error);
  }
};

const getStudents = async () => {
  try {
    const responce = await api.get("/students/");
    students.value = responce.data;
  } catch (error) {
    console.error("Ошибка при получении студентов:", error);
  }
};

const toggleSelectAllInstructors = () => {
  if (selectAllInstructors.value)
    selectedInstructors.value = instructors.value.map(
      (instructor) => instructor.id
    );
  else selectedInstructors.value = [];
};

const toggleSelectAllStudents = () => {
  if (selectAllStudents.value)
    selectedStudents.value = students.value.map((student) => student.id);
  else selectedStudents.value = [];
};

const updateSelectAllState = computed(() => {
  selectAllInstructors.value =
    instructors.value.length > 0 &&
    selectedInstructors.value.length === instructors.value.length;
});

onMounted(async () => {
  await getInstructors();
  await getStudents();
});
</script>

<style scoped>
table {
  width: 90%;
  border-collapse: collapse;
  margin: 20px 0;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

th {
  background-color: #f4f4f4;
  text-align: center;
}

ul {
  padding: 0;
  margin: 0;
  list-style: none;
}

.table__container {
  display: flex;
  justify-content: center;
}
</style>
