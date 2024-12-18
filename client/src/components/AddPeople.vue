<template>
  <div class="modal__backdrop" @click="$emit('close')">
    <div class="modal__window" @click.stop>
      <div class="card__container">
        <h1>{{ cardTitle }}</h1>
        <div class="image__select">
          <input
            ref="fileUp"
            @change="fileSelect"
            type="file"
            style="display: none"
          />
          <img
            v-if="!imageSrc"
            @click="selectImg"
            src="/src/assets/person-add.png"
            alt="Добавить фото"
          />
          <img v-else @click="selectImg" :src="imageSrc" alt="Добавить фото" />
        </div>
        <div class="info__container">
          <div class="info__textbox">
            <span>Фамилия</span>
            <input
              v-model="lastName"
              type="text"
              placeholder="Введите фамилию"
              required
            />
          </div>
          <div class="info__textbox">
            <span>Имя</span>
            <input
              v-model="firstName"
              type="text"
              placeholder="Введите имя"
              required
            />
          </div>
          <div class="info__textbox">
            <span>Дата рождения</span>
            <input
              v-model="birthDate"
              type="date"
              placeholder="Выберите дату рождения"
              required
            />
          </div>
          <div class="info__textbox">
            <span>Кафедра</span>
            <select v-model="selectedDepartment">
              <option value="notSelected">Выберите кафедру...</option>
              <option
                v-for="department in departments"
                :key="department.department_id"
                :value="department.department_id"
              >
                {{ department.department_name }}
              </option>
            </select>
          </div>
        </div>
        <div class="actions">
          <button @click="save">Ок</button>
          <button @click="$emit('close')">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, defineProps, defineEmits } from "vue";
import api from "@/services/api";
import { useToast } from "vue-toastification";

const toast = useToast();
const props = defineProps({
  category: {
    required: true,
  },
});

const emit = defineEmits(["close"]);

const fileUp = ref(null);
const imageSrc = ref("");
const lastName = ref("");
const firstName = ref("");
const birthDate = ref("");
const selectedDepartment = ref("notSelected");

let cardTitle = ref("");
let departments = ref([]);

const getDepartments = async () => {
  try {
    const responce = await api.get("/departments/");
    departments.value = responce.data;
  } catch (error) {
    console.error("Ошибка при получении кафедр:", error);
  }
};

const fileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();

    reader.onload = (e) => {
      imageSrc.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const selectImg = () => {
  fileUp.value.click();
};

const save = async () => {
  if (
    !lastName.value ||
    !firstName.value ||
    !birthDate.value ||
    selectedDepartment.value === "notSelected"
  ) {
    toast.error("Пожалуйста, заполните все поля.");
    return;
  }

  const formData = {
    last_name: lastName.value,
    first_name: firstName.value,
    birth_date: birthDate.value,
    photo: imageSrc.value,
  };

  try {
    if (props.category === "instructors") {
      formData.department_id = selectedDepartment.value;
      await api.post("/instructors/add/", formData);
    } else if (props.category === "students") {
      await api.post(
        `/students/add/?department_id=${selectedDepartment.value}`,
        formData
      );
    }

    toast.success("Данные успешно сохранены!");
    emit("close");
  } catch (error) {
    console.error(error);
    if (error.response) {
      const errorResponseData = error.response.data;
      const serverMessage =
        errorResponseData.detail[0].msg || errorResponseData.detail;
      toast.error(`Ошибка: ${serverMessage}`);
    } else {
      toast.error("Произошла ошибка при отправке запроса.");
    }
  }
};

onMounted(() => {
  cardTitle.value =
    props.category === "instructors"
      ? "Карточка Преподавателя"
      : "Карточка Студента";
  getDepartments();
});
</script>

<style scoped>
.modal__backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal__window {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  padding: 20px;
  width: 500px;
  max-width: 90%;
  z-index: 1010;
}

.card__container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.image__select {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.image__select img {
  width: 300px;
}

.info__container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: end;
  margin-bottom: 20px;
}

.info__textbox {
  display: flex;
  gap: 10px;
  font-size: 20px;
}

.info__textbox input {
  width: 300px;
  border: none;
  border-bottom: 1px solid rgb(68, 68, 68);
  padding: 0 5px;
  font-size: 20px;
}

select {
  font-size: 20px;
  background-color: white;
  border-radius: 2px;
  border: 1px solid rgb(68, 68, 68);
  padding: 0 8px;
  width: 300px;
}

.actions {
  display: flex;
  gap: 20px;
}
.actions button {
  font-size: 20px;
  border-radius: 5px;
  padding: 3px 5px;
  width: 100px;
  border: 1px solid rgb(68, 68, 68);
}
</style>
