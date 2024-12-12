<template>
  <div class="side_bar">
    <div class="buttons_container">
      <div class="buttons-filters">
        <div class="container">
          <div
            class="buttons"
            :class="{ active: activeButton === 'instructorButtons' }"
            @click="toggleButtons('instructorButtons')"
          >
            <button class="people_btn">Преподаватели</button>
            <button
              class="filter_btn"
              @click.stop="toggleFilters('instructorFilters', 'instructorButtons')"
            >
              <img src="/src/assets/filter.png" alt="" />
            </button>
          </div>
        </div>
        <FiltersItems v-if="visibleFilters === 'instructorFilters'" />
      </div>

      <div class="buttons-filters">
        <div class="container">
          <div
            class="buttons"
            :class="{ active: activeButton === 'studentButtons' }"
            @click="toggleButtons('studentButtons')"
          >
            <button class="people_btn">Студенты</button>
            <button
              class="filter_btn"
              @click.stop="toggleFilters('studentFilters', 'studentButtons')"
            >
              <img src="/src/assets/filter.png" alt="" />
            </button>
          </div>
        </div>
        <FiltersItems v-if="visibleFilters === 'studentFilters'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from "vue";
import FiltersItems from "./FiltersItems.vue";

const emit = defineEmits(["category-changed"]);
const activeButton = ref("instructorButtons");
const visibleFilters = ref(null);

const toggleFilters = (filter, button) => {
  toggleButtons(button);
  visibleFilters.value = visibleFilters.value === filter ? null : filter;
};

const toggleButtons = (button) => {
  if (activeButton.value !== button) {
    activeButton.value = button;
    visibleFilters.value = null;
    emit("category-changed", button)
  }
};
</script>

<style scoped>
.side_bar {
  height: 100vh;
  width: 400px;
  background-color: rgb(211, 170, 248);
}

.buttons_container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 100px;
}

img {
  width: 24px;
}

.container {
  display: flex;
  flex-direction: column;
}

.container button {
  font-size: 20px;
  background-color: #ffffff;
}

.people_btn {
  padding: 8px 24px;
  border-radius: 5px 0 0 5px;
  border: none;
  width: 200px;
}

.filter_btn {
  padding: 0 10px;
  border-radius: 0 5px 5px 0;
  border: none;
}

.buttons {
  display: flex;
  gap: 1px;
  opacity: 0.5;
}

.buttons.active {
  opacity: 1;
}

.buttons-filters {
  display: flex;
  flex-direction: column;
  align-items: end;
  gap: 5px;
  margin-right: 10px;
}
</style>
