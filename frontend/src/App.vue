<script setup>
import ArrowBackButton from './components/ArrowBackButton.vue'
import ArrowNextButton from './components/ArrowNextButton.vue'
import HomeButton from './components/HomeButton.vue'
import KeyframePage from './components/KeyframePage.vue'
import KeyframePrompt from './components/KeyframePrompt.vue'
import ScenarioSection from './components/ScenarioSection.vue'
import VideoPage from './components/VideoPage.vue'
</script>

<template>
  <div class="app-container">
    <HomeButton />
    <ArrowBackButton />
    <ArrowNextButton />
    <KeyframePage />
    <KeyframePrompt />
    <ScenarioSection />
    <VideoPage />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
}
</style>

