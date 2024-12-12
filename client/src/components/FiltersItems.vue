<template>
  <div>
    <div v-if="departments.length > 0">
      <div class="filters-container">
        <p @click="toggleDepartments" class="dropdown-header">Кафедры</p>
        <div v-if="showDepartments" class="dropdown-content">
          <div
            class="checkbox-item"
            v-for="(department, index) in departments"
            :key="index"
          >
            <input type="checkbox" />
            <p>{{ department }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div>
    <div v-if="groups.length > 0">
      <div class="filters-container">
        <p @click="toggleGroups" class="dropdown-header">Группы</p>
        <div v-if="showGroups" class="dropdown-content">
          <div
            class="checkbox-item"
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
    departments.value = responce.data.departments_name;
    console.log(departments.value);
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
.checkbox-item {
  display: flex;
  gap: 5px;
}

.dropdown-header {
  cursor: pointer;
  background-color: #ffffff;
  border-radius: 5px;
  padding: 10px 40px;
  text-align: center;
  width: 230px;
}

.dropdown-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 5px;
  padding: 5px 10px;
  border-radius: 5px;
  background-color: #ffffff;
}

.filters-container {
  display: flex;
  flex-direction: column;
  align-items: end;
}
</style>
