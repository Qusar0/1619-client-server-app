<template>
    <SideBar @category-changed="onCategoryChanged" />
    <router-view :key="category" :category="category" />
  </template>
  
  <script setup>
  import { ref, provide } from "vue";
  import SideBar from "@/components/SideBar.vue";
  
  const category = ref("instructors");
  
  provide('category', category);
  provide('onCategoryChanged', (newCategory) => {
    category.value = newCategory;
  });
  
  const onCategoryChanged = (newCategory) => {
    category.value = newCategory;
  };
  </script>
  