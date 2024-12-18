<template>
  <div>
    <div v-if="departments.length > 0">
      <div class="filters__container">
        <p @click="toggleDepartments" class="dropdown__header">Кафедры</p>
        <div v-if="showDepartments" class="dropdown__content">
          <div
            class="checkbox__item"
            v-for="department in departments"
            :key="department.department_id"
          >
            <input type="checkbox" />
            <p>{{ department.department_name }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div>
    <div v-if="groups.length > 0">
      <div class="filters__container">
        <p @click="toggleGroups" class="dropdown__header">Группы</p>
        <div v-if="showGroups" class="dropdown__content">
          <div
            class="checkbox__item"
            v-for="(group, index) in groups"
            :key="index"
          >
            <input type="checkbox" />
            <p>{{ group }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import api from "@/services/api";
import { onMounted, ref } from "vue";

let departments = ref([]);
let groups = ref([]);
let showDepartments = ref(false);
let showGroups = ref(false);

const getDepartments = async () => {
  try {
    const responce = await api.get("/departments/");
    console.log(responce.data);
    departments.value = responce.data;
    console.log(departments);
  } catch (error) {
    console.error("Ошибка при получении кафедр:", error);
  }
};

const getGroups = async () => {
  try {
    const responce = await api.get("/groups/");
    groups.value = responce.data.groups_name;
    console.log(groups.value);
  } catch (error) {
    console.error("Ошибка при получении групп:", error);
  }
};

const toggleDepartments = () => {
  showDepartments.value = !showDepartments.value;
};

const toggleGroups = () => {
  showGroups.value = !showGroups.value;
};

onMounted(async () => {
  await getDepartments();
  await getGroups();
});
</script>

<style scoped>
.checkbox__item {
  display: flex;
  gap: 5px;
}

.dropdown__header {
  cursor: pointer;
  background-color: #ffffff;
  border-radius: 5px;
  padding: 10px 40px;
  text-align: center;
  width: 230px;
}

.dropdown__content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 5px;
  padding: 5px 10px;
  border-radius: 5px;
  background-color: #ffffff;
  max-height: 200px;
  overflow-y: auto;
}

.filters__container {
  display: flex;
  flex-direction: column;
  align-items: end;
}
</style>
