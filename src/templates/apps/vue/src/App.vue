<script setup>
const projectName = "$$NAME$$";
const description = "$$DESCRIPTION$$";
const language = "$$LANGUAGE$$";
const framework = "$$FRAMEWORK$$";
</script>

<template>
    <main>
        <h1>{{ projectName }}</h1>
        <p>{{ description }}</p>
        <small>{{ language }} / {{ framework }}</small>
    </main>
</template>
