<template>
  <div class="main__container">
    <div class="activity__container">
      <div class="search__container">
        <img src="/src/assets/search.svg" alt="Лупа" />
        <input class="search__input" type="text" placeholder="Поиск..." />
      </div>
      <div class="activity__buttons">
        <button class="delete__button">Удалить</button>
        <button class="add__button" @click="openAddModal">Добавить</button>
      </div>
    </div>
    <TableItems :category="category" :data="data" />
    <div
      v-if="isAddModalOpen"
      class="modal__backdrop"
      @click.self="closeAddModal"
    >
      <div class="modal__content">
        <AddPeople :category="category" @close="closeAddModal" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, onBeforeUnmount, onMounted, ref } from "vue";
import TableItems from "@/components/TableItems.vue";
import AddPeople from "@/components/AddPeople.vue";

const category = inject("category");
const isAddModalOpen = ref(false);
const data = ref(null);

const openAddModal = () => {
  isAddModalOpen.value = true;
};

const closeAddModal = () => {
  isAddModalOpen.value = false;
};

const socket = ref(null);

const initializeWebSocket = () => {
  socket.value = new WebSocket("ws://localhost:8000/ws/updates");

  socket.value.onopen = () => {
    console.log("WebSocket соединение открыто.");
  };

  socket.value.onmessage = (event) => {
    try {
      const updatedData = JSON.parse(event.data);
      if (updatedData.category === category.value) {
        console.log("Обновление данных через WebSocket:", updatedData);
        data.value = updatedData.data;
        console.log(data.value);
      }
    } catch (e) {
      console.error("Ошибка парсинга JSON:", e);
      console.log("Получено сообщение:", event.data);
    }
  };

  socket.value.onclose = () => {
    console.log("WebSocket соединение закрыто.");
  };

  socket.value.onerror = (error) => {
    console.error("Ошибка WebSocket:", error);
  };
};

onMounted(() => {
  initializeWebSocket();
});

onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close();
    console.log("WebSocket соединение закрыто при уничтожении компонента.");
  }
});
</script>

<style scoped>
.main__container {
  width: 100%;
  margin-top: 50px;
}

.activity__container {
  display: flex;
  justify-content: space-around;
}

.search__container {
  position: relative;
}

.search__container img {
  position: absolute;
  left: 7px;
  top: 7px;
}

.search__input {
  padding: 4px 30px;
  border-radius: 5px;
  border: 1px solid rgb(68, 68, 68);
  font-size: 18px;
}

.activity__buttons {
  display: flex;
  gap: 20px;
}

.activity__buttons button {
  padding: 5px 8px;
  border-radius: 5px;
  border: 1px solid rgb(68, 68, 68);
  font-size: 18px;
  color: white;
}

.delete__button {
  background-color: rgb(255, 14, 14);
}

.delete__button:hover {
  background-color: rgb(180, 0, 0);
}

.add__button {
  background-color: rgb(0, 202, 27);
}

.add__button:hover {
  background-color: rgb(0, 153, 20);
}
</style>
