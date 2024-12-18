<template>
  <div class="table__container">
    <table>
      <thead>
        <tr>
          <th></th>
          <th>Фамилия Имя</th>
          <th>Кафедра</th>
          <th v-if="category === 'instructors'">Группы</th>
          <th v-if="category === 'students'">Группa</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in data" :key="item.id">
          <td>
            <input
              type="checkbox"
              :value="item.id"
              :checked="isSelected(item.id)"
              @change="toggleSelection(item.id)"
            />
          </td>
          <td>{{ item.first_name }} {{ item.last_name }}</td>
          <td>{{ item.department }}</td>
          <td v-if="category === 'instructors'">
            <ul>
              <li v-for="group in item.groups" :key="group.id">
                {{ group }}
              </li>
            </ul>
          </td>
          <td v-if="category === 'students'">
            {{ item.group }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  category: String,
  data: Array,
  selected: Array,
});

const emit = defineEmits(["update:selected"]);

const isSelected = (id) => {
  return props.selected.includes(id);
};

const toggleSelection = (id) => {
  const newSelected = [...props.selected];
  const index = newSelected.indexOf(id);
  if (index === -1) {
    newSelected.push(id);
  } else {
    newSelected.splice(index, 1);
  }
  emit("update:selected", newSelected);
};
</script>

<style scoped>
.table__container {
  display: flex;
  justify-content: center;
  max-height: 600px;
  overflow-y: auto;
  margin: 20px auto;
}

table {
  width: 90%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

th {
  background-color: #f4f4f4;
  position: sticky;
  top: -1px;
  z-index: 2;
}

ul {
  padding: 0;
  margin: 0;
  list-style: none;
}
</style>
