<template>
  <div>
    <Table
      v-if="category === 'instructors'"
      :category="category"
      :data="instructors"
      :selected="selectedInstructors"
      @update:selected="selectedInstructors = $event"
    />
    <Table
      v-if="category === 'students'"
      :category="category"
      :data="students"
      :selected="selectedStudents"
      @update:selected="selectedStudents = $event"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import api from "@/services/api";
import Table from "./Table.vue";

const props = defineProps({
  category: String,
  data: Array,
});

const emit = defineEmits(["refresh"]);

const instructors = ref(props.data || []);
let selectedInstructors = ref([]);

const students = ref(props.data || []);
let selectedStudents = ref([]);

const getInstructors = async () => {
  try {
    const response = await api.get("/instructors/");
    instructors.value = response.data;
  } catch (error) {
    console.error("Ошибка при получении кураторов:", error);
  }
};

const getStudents = async () => {
  try {
    const response = await api.get("/students/");
    students.value = response.data;
  } catch (error) {
    console.error("Ошибка при получении студентов:", error);
  }
};

watch(
  () => props.data,
  (newData) => {
    if (props.category === "instructors") {
      instructors.value = newData;
    } else if (props.category === "students") {
      students.value = newData;
    }
  }
);

onMounted(() => {
  if (props.category === "instructors") {
    if (props.data) {
      instructors.value = props.data;
    } else {
      getInstructors();
    }
  } else if (props.category === "students") {
    if (props.data) {
      students.value = props.data;
    } else {
      getStudents();
    }
  }
});
</script>
