<template>
  <div class="main-container">
    <div class="activity-container">
      <div class="search-container">
        <img class="" src="/src/assets/search.svg" alt="Лупа" />
        <input class="search-input" type="text" placeholder="Поиск..." />
      </div>
      <div class="activity-buttons">
        <button class="delete-button">Уволить</button>
        <button class="add-button">Нанять</button>
      </div>
    </div>
    <TableItems />
  </div>
</template>

<script setup>
import TableItems from "@/components/TableItems.vue";
</script>
<style scoped>
.main-container {
  width: 100%;
  margin-top: 50px;
}
.activity-container {
  display: flex;
  justify-content: space-around;
}
.search-container {
  position: relative;
}

.search-container img {
  position: absolute;
  left: 7px;
  top: 7px;
}

.search-input {
  padding: 4px 30px;
  border-radius: 5px;
  border: 1px solid rgb(68, 68, 68);
  font-size: 18px;
}

.activity-buttons {
  display: flex;
  gap: 20px;
}

.activity-buttons button {
  padding: 5px 8px;
  border-radius: 5px;
  border: 1px solid rgb(68, 68, 68);
  font-size: 18px;
  color: white;
}

.delete-button {
  background-color: rgb(255, 14, 14);
}

.delete-button:hover {
  background-color: rgb(180, 0, 0);
}

.add-button {
  background-color: rgb(0, 202, 27);
}

.add-button:hover {
  background-color: rgb(0, 153, 20);
}
</style>
