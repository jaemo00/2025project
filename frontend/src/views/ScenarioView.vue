<template>
  <div class="min-h-screen flex flex-col items-center bg-[#12100E] px-4 md:px-8 xl:px-12 py-12 text-gray-100">
    <div
      class="bg-[#1A1816] rounded-xl shadow-xl p-8 w-full
             max-w-5xl lg:max-w-6xl xl:max-w-7xl 2xl:max-w-[90rem]
             space-y-6 border border-[#FFB224]/20">
      <h1 class="text-2xl font-bold text-center text-[#FFB224]">시나리오 생성</h1>

      <!-- 0) 모드 선택 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button type="button" @click="mode = 'with-char'" :class="cardClass(mode === 'with-char')">
          <div class="text-left space-y-2">
            <div class="text-lg font-semibold text-[#FFB224]">캐릭터 포함 시나리오</div>
            <p class="text-sm text-gray-300">Topic/Description/주요 캐릭터/캐릭터 설명 + 캐릭터 이미지</p>
          </div>
        </button>
        <button type="button" @click="mode = 'no-char'" :class="cardClass(mode === 'no-char')">
          <div class="text-left space-y-2">
            <div class="text-lg font-semibold text-[#FFB224]">캐릭터 없이 시나리오</div>
            <p class="text-sm text-gray-300">Topic/Description만으로 진행 · 컷별 프롬프트/이미지</p>
          </div>
        </button>
      </div>

      <!-- 1) 주제 입력 -->
      <div class="space-y-2">
        <label class="text-sm text-gray-300">입력</label>
        <textarea
          v-model="user_input"
          :disabled="isBusy"
          placeholder="주제 및 영상 시간(5초 단위)을 입력해주세요"
          class="w-full h-28 p-4 rounded-md resize-none bg-[#12100E] text-gray-100 placeholder-gray-400 
                 border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
        ></textarea>
        <p class="text-xs text-gray-400">* 모드를 선택하고 주제를 입력한 뒤 <strong>시작하기</strong>를 누르세요.</p>
      </div>

      <!-- 1-1) 영상 길이 선택 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="md:col-span-1">
          <label class="text-sm text-gray-300">영상 길이</label>
          <select
            v-model.number="durationSec"
            :disabled="isBusy"
            class="w-full p-3 rounded-md bg-[#12100E] text-gray-100 border border-[#FFB224]/30
                   focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            title="5~60초까지 5초 간격으로 선택"
          >
            <option v-for="sec in durationOptions" :key="sec" :value="sec">{{ sec }}초</option>
          </select>
        </div>
        <div class="md:col-span-2 flex items-end">
          <p class="text-xs text-gray-400">
            * 5초~60초(5초 단위). 길이는 초안 구성과 컷 수(2.5초/컷 기준)에 영향을 줄 수 있습니다.
          </p>
        </div>
      </div>

      <!-- 2) 시작하기 = 초안 받아오기 -->
      <div class="flex gap-3">
        <button
          :disabled="draftLoading || !user_input.trim() || !mode"
          @click="fetchScenarioDraft"
          class="flex-1 bg-[#FFB224] text-[#12100E] py-2 rounded font-semibold 
                 hover:bg-[#e6a020] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="draftLoading">초안 생성 중…</span>
          <span v-else>시작하기</span>
        </button>

        <!-- 기존 프로젝트 불러오기 -->
        <button
          @click="fetchProjects"
          class="flex-1 bg-transparent text-[#FFB224] py-2 rounded font-semibold 
                 border border-[#FFB224]/60 hover:bg-[#FFB224]/10 transition-colors"
        >
          기존 프로젝트 불러오기
        </button>
      </div>

      <!-- 3) 초안 편집 -->
      <div v-if="draftVisible" class="w-full bg-[#1A1816] rounded-xl shadow-xl p-6 space-y-4 border border-[#FFB224]/20">
        <h2 class="text-xl font-bold text-[#FFB224]">시나리오 초안</h2>

        <div class="grid gap-3 md:grid-cols-2">
          <div class="grid gap-2">
            <label class="text-sm text-gray-300">주제</label>
            <input
              v-model="draft.kor_topic"
              :disabled="isBusy"
              class="w-full p-3 rounded-md bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            />
          </div>

          <div class="grid gap-2" v-if="mode==='with-char'">
            <label class="text-sm text-gray-300">메인 캐릭터</label>
            <input
              v-model="draft.main_character"
              :disabled="isBusy"
              class="w-full p-3 rounded-md bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            />
          </div>
        </div>

        <div class="grid gap-3 md:grid-cols-2">
          <div class="grid gap-2">
            <label class="text-sm text-gray-300">설명</label>
            <textarea
              v-model="draft.kor_description"
              :disabled="isBusy"
              rows="4"
              class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            ></textarea>
          </div>

          <div class="grid gap-2" v-if="mode==='with-char'">
            <label class="text-sm text-gray-300">메인 캐릭터 설명</label>
            <textarea
              v-model="draft.main_character_description"
              :disabled="isBusy"
              rows="4"
              class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            ></textarea>
          </div>
        </div>

        <!-- with-char: 캐릭터 이미지 패널 열기 버튼 -->
        <div v-if="mode==='with-char'" class="flex items-center justify-end pt-2">
          <button
            type="button"
            :disabled="isBusy"
            @click="openCharacterPanel"
            class="px-4 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                   hover:bg-[#FFB224]/10 transition-colors"
          >
            캐릭터 이미지 만들기
          </button>
        </div>

        <!-- with-char 전용: 캐릭터 이미지 프롬프트 패널 (버튼을 눌러야 보임) -->
        <div v-if="charPanelVisible" class="mt-4 space-y-4 border-t border-[#FFB224]/20 pt-4">
          <h3 class="text-lg font-semibold text-[#FFB224] flex items-center gap-2">
            캐릭터 이미지
            <span v-if="charPromptLoading" class="text-xs text-gray-400">AI 프롬프트 생성 중…</span>
          </h3>

          <!-- 모델/사이즈 -->
          <div class="flex flex-wrap items-center gap-3">
            <label class="text-sm text-gray-300">모델</label>
            <select v-model="charModel"
                    class="bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm">
              <option value="sdxl">Stable Diffusion XL</option>
              <option value="dalle-3">DALL·E 3</option>
            </select>

            <label class="text-sm text-gray-300 ml-2">사이즈</label>
            <input type="number" v-model.number="charWidth" min="256" step="64"
                   class="w-24 bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm" placeholder="W" />
            <span class="text-gray-400 text-sm">×</span>
            <input type="number" v-model.number="charHeight" min="256" step="64"
                   class="w-24 bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm" placeholder="H" />
          </div>

          <!-- 프롬프트 -->
          <div class="grid gap-2">
            <label class="text-sm text-gray-300">Character Image Prompt
              <span class="ml-1 text-[11px] text-gray-500">(AI 자동 생성, 바로 수정 가능)</span>
            </label>
            <textarea
              v-model="charImgPrompt"
              @input="charPromptDirty = true"
              :disabled="scenesLoading || finalizing"
              rows="3"
              placeholder="자동 생성 프롬프트 또는 직접 입력/수정"
              class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            ></textarea>
          </div>

          <!-- 생성 버튼 -->
          <div class="flex flex-wrap gap-3">
            <button
              type="button"
              :disabled="charImgLoading || (!charImgPrompt.trim())"
              @click="generateCharacterImage"
              class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E]
                     hover:bg-[#e6a020] disabled:opacity-50 transition-colors"
            >
              <span v-if="charImgLoading">캐릭터 이미지 생성 중…</span>
              <span v-else>캐릭터 이미지 생성하기</span>
            </button>
          </div>

          <!-- 미리보기 -->
          <div v-if="charImgUrl" class="pt-2">
            <div class="text-sm text-gray-300 mb-2">미리보기</div>
            <img :src="charImgUrl" alt="character" class="w-full max-h-[28rem] object-contain rounded-lg border border-[#FFB224]/20" />
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-4">
          <button
            type="button"
            :disabled="isBusy"
            @click="draftVisible = false"
            class="px-4 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                   hover:bg-[#FFB224]/10 transition-colors"
          >
            취소
          </button>

          <!-- 4) 시나리오 생성하기 -->
          <button
            type="button"
            :disabled="scenesLoading || finalizing"
            @click="generateScenario"
            class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E] 
                   hover:bg-[#e6a020] disabled:opacity-50 transition-colors"
          >
            <span v-if="scenesLoading">컷 생성 중…</span>
            <span v-else>시나리오 생성하기</span>
          </button>
        </div>
      </div>

      <!-- 5) 번호별 컷 편집 -->
      <div v-if="scenesVisible" class="w-full bg-[#1A1816] rounded-xl shadow-xl p-6 space-y-4 border border-[#FFB224]/20">
        <h2 class="text-xl font-bold text-[#FFB224]">컷 편집</h2>
        <p class="text-sm text-gray-400">* 마음에 들지 않는 컷은 자유롭게 수정하세요.</p>

        <div class="space-y-4 max-h-[60vh] overflow-auto pr-1">
          <div
            v-for="(s, idx) in contents"
            :key="idx"
            class="bg-[#12100E]/60 p-4 rounded border border-[#FFB224]/20"
          >
            <label class="text-sm font-semibold text-[#FFB224] block mb-2">#{{ idx+1 }}</label>
            <textarea
              v-model="contents[idx]"
              rows="3"
              class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500
                     border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
            ></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            @click="scenesVisible = false"
            class="px-4 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                   hover:bg-[#FFB224]/10 transition-colors"
          >
            뒤로
          </button>
          <button
            type="button"
            :disabled="finalizing"
            @click="confirmScenario"
            class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E] 
                   hover:bg-[#e6a020] disabled:opacity-50 transition-colors"
          >
            이 컷들로 확정
          </button>
        </div>
      </div>

      <!-- 5-2) 키프레임 프롬프트 & 이미지 -->
      <div v-if="keyframesVisible" class="w-full bg-[#1A1816] rounded-xl shadow-xl p-6 space-y-4 border border-[#FFB224]/20">
        <h2 class="text-xl font-bold text-[#FFB224]">키프레임 컷</h2>
        <p class="text-sm text-gray-400">
          * 각 2.5초에 대응하는 단일 이미지 프롬프트입니다. 프롬프트를 수정하고 생성/재생성을 눌러 이미지를 만듭니다.
        </p>

        <div class="flex items-center gap-3">
          <button
            type="button"
            :disabled="keyframesLoading || !keyframePrompts.length"
            @click="generateAllKeyframePrompts"
            class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E]
                   hover:bg-[#e6a020] disabled:opacity-50 transition-colors"
          >
            <span v-if="keyframesLoading">프롬프트 생성 중…</span>
            <span v-else>프롬프트 생성</span>
          </button>
          <button
            type="button"
            @click="keyframesVisible = false"
            class="px-4 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                   hover:bg-[#FFB224]/10 transition-colors"
          >
            뒤로
          </button>
        </div>

        <div class="space-y-4 max-h-[60vh] overflow-auto pr-1">
          <div
            v-for="(kf, idx) in keyframePrompts"
            :key="idx"
            class="bg-[#12100E]/60 p-4 rounded border border-[#FFB224]/20"
          >
            <div class="flex items-center justify-between mb-3">
              <div class="text-[#FFB224] font-semibold">#{{ idx+1 }}</div>

              <div class="flex items-center gap-2">
                <select v-model="kf.model"
                        class="bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm">
                  <option value="sdxl">Stable Diffusion XL</option>
                  <option value="dalle-3">DALL·E 3</option>
                </select>
                <input type="number" v-model.number="kf.width" min="256" step="64"
                       class="w-20 bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm"
                       placeholder="W" />
                <span class="text-gray-400 text-sm">×</span>
                <input type="number" v-model.number="kf.height" min="256" step="64"
                       class="w-20 bg-[#12100E] border border-[#FFB224]/40 rounded px-2 py-1 text-sm"
                       placeholder="H" />
              </div>
            </div>

            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-gray-400 mb-2 whitespace-pre-line">Content: {{ kf.content }}</div>
                <textarea
                  v-model="kf.prompt"
                  rows="3"
                  class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500
                         border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224] focus:border-transparent"
                  placeholder="이 컷을 한 문장으로 정확히 묘사하는 프롬프트"
                ></textarea>

                <div class="flex flex-wrap gap-2 mt-3">
                  <button
                    type="button"
                    :disabled="kf.imgLoading"
                    @click="generateKeyframeImage(idx)"
                    class="text-sm px-3 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                           hover:bg-[#FFB224]/10 transition-colors"
                  >
                    <span v-if="kf.imgLoading">이미지 생성 중…</span>
                    <span v-else>이미지 생성</span>
                  </button>

                  <button
                    type="button"
                    :disabled="kf.imgLoading || !kf.seriesIndex"
                    @click="regenKeyframeImage(idx)"
                    class="text-sm px-3 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                           hover:bg-[#FFB224]/10 transition-colors disabled:opacity-50"
                  >
                    <span v-if="kf.imgLoading">이미지 재생성 중…</span>
                    <span v-else>이미지 재생성</span>
                  </button>
                </div>
              </div>

              <div class="flex flex-col items-center justify-center border border-[#FFB224]/20 rounded p-3">
                <template v-if="kf.imageUrl">
                  <img :src="kf.imageUrl" alt="keyframe"
                       class="w-full max-h-80 object-contain rounded-lg border border-[#FFB224]/20" />
                  <div class="text-xs text-gray-500 mt-2">tries {{ kf.seriesIndex || 0 }} | {{ kf.model }} | {{ kf.width }}×{{ kf.height }}</div>
                </template>
                <template v-else>
                  <div class="text-sm text-gray-500">아직 이미지가 없습니다.</div>
                </template>
                <!-- ✅ 진행률 바 -->
                <div
                  v-if="kf.imgLoading &&kf.model==='sdxl'"
                  class="mt-4"
                >
                  <div class="flex justify-between text-xs text-gray-400 mb-1">
                    <span>키프레임 생성 진행률</span>
                    <span>{{ imgProgress }}%</span>
                  </div>
                  <div class="w-full h-2 bg-gray-800 rounded overflow-hidden">
                    <div
                      class="h-2 bg-[#FFB224] transition-all"
                      :style="{ width: imgProgress + '%' }"
                    ></div>
                  </div>
                </div>
            </div>
          </div>
        </div>

        <!-- 기존 '프롬프트 확정' 버튼 → '비디오 만들기'로 대체 -->
        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            :disabled="keyframesLoading"
            @click="makeVideo"
            class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E]
                   hover:bg-[#e6a020] disabled:opacity-50 transition-colors"
          >
            비디오 만들기
          </button>
        </div>
      </div>


      <!-- 다음 단계 (키프레임 단계로 진입하는 버튼은 이전 단계에만 표기) -->
      <div v-if="!keyframesVisible" class="text-center pt-2">
        <button
          :disabled="!scenario"
          @click="goNext"
          class="px-4 py-2 rounded font-semibold 
                 bg-transparent text-[#FFB224] border border-[#FFB224]/60 
                 hover:bg-[#FFB224]/10 transition-colors disabled:opacity-50"
        >
          키프레임 생성으로 이동 →
        </button>
      </div>
    </div>

    <!-- 프로젝트 목록 -->
    <div
      v-if="Object.keys(groupedProjects).length > 0 && !keyframesVisible"
      class="mt-10 w-full max-w-5xl lg:max-w-6xl xl:max-w-7xl 2xl:max-w-[90rem]">
      <h2 class="text-xl font-bold text-[#FFB224] mb-4">저장된 프로젝트</h2>
      <div v-for="(items, date) in groupedProjects" :key="date" class="mb-6">
        <h3 class="text-md font-semibold text-gray-300 mb-2">{{ date }}</h3>
        <div class="space-y-2">
          <div
            v-for="project in items"
            :key="project.projectId || project.project_id"
            class="flex justify-between items-center bg-[#1A1816] p-4 rounded-lg shadow 
                   border border-[#FFB224]/20 hover:border-[#FFB224]/40 transition-colors"
          >
            <span class="font-medium text-gray-100">{{ project.title }}</span>
            <button @click="enterProject(project.projectId || project.project_id)" class="text-[#FFB224] hover:underline">불러오기</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/appStore'
import axios from 'axios'

const NEXT_ROUTE = '/keyframes'

/* -------------------------
   상태
------------------------- */
const mode = ref(null) // 'with-char' | 'no-char' | null
const user_input = ref('')
const scenario = ref(null)
const projects = ref([])

const draftVisible = ref(false)
const draftLoading = ref(false)

const scenesVisible = ref(false)
const scenesLoading = ref(false)
const finalizing = ref(false)

const draft = ref({
  topic: '',
  description: '',
  kor_topic: '',
  kor_description: '',
  main_character: '',
  main_character_description: ''
})

const imgProgress = computed(() => Number(store.imgProgress || 0))
const contents = ref([]) // [{ no, text }]

/* with-char: 캐릭터 이미지 프롬프트 패널 */
const charPanelVisible = ref(false)
const charImgPrompt = ref('')
const charImgUrl = ref('')
const charPromptLoading = ref(false)
const charPromptDirty = ref(false)
const charImgLoading = ref(false)
const charModel = ref('dalle-3') 
const charWidth = ref(1024)
const charHeight = ref(1024)

/* 키프레임: 프롬프트 & 이미지 */
const keyframesVisible = ref(false)
const keyframesLoading = ref(false)
/*
  keyframePrompts item:
  {
    no, content, prompt, imageUrl,
    imgLoading, model, width, height,
    seriesIndex
  }
*/
const keyframePrompts = ref([])

/* 영상 길이(초): 5~60, 5초 간격 */
const durationSec = ref(10)
const durationOptions = Array.from({ length: 12 }, (_, i) => (i + 1) * 5)

const store = useAppStore()
const router = useRouter()
const isBusy = computed(() => draftLoading.value || scenesLoading.value || finalizing.value || charPromptLoading.value)

/* -------------------------
   유틸
------------------------- */
function cardClass(active) {
  return [
    'p-4 rounded-xl border transition',
    active ? 'border-[#FFB224] bg-[#12100E]/60' : 'border-[#FFB224]/20 bg-[#12100E]/40 hover:border-[#FFB224]/40'
  ]
}
function showError(e, fallback = '요청에 실패했습니다.') {
  const msg = e?.response?.data?.detail || e?.message || fallback
  alert(msg)
}


function normalizeImageUrl(p) {
  if (!p) return ''
  let s = String(p).replaceAll('\\', '/')
  if (/^https?:|^data:/.test(s)) return s
  if (s.includes('/temp/')) s = s.slice(s.indexOf('/temp/'))
  if (!s.startsWith('/')) s = '/' + s
  return s
}






onMounted(() => {
  if (store.scenario) {
    scenario.value = store.scenario
    user_input.value = store.scenario?.info?.title ?? user_input.value
  }
  if (store.characterImage) {
    charImgUrl.value = store.characterImage.url || ''
    charImgPrompt.value = store.characterImage.prompt || ''
  }
  const saved = Number(sessionStorage.getItem('project_id'))
  if (!store.project_id && Number.isInteger(saved) && saved > 0) {
    store.project_id = saved
  }
  if (store.scenario?.info?.timeSec) {
    durationSec.value = Number(store.scenario.info.timeSec) || durationSec.value
  }
})

watch(() => store.project_id, (pid) => {
  const n = Number(pid)
  if (Number.isInteger(n) && n > 0) {
    sessionStorage.setItem('project_id', String(n))
  }
})

/* -------------------------
   캐릭터 패널 오픈 → AI 프롬프트 자동 채움(안전)
------------------------- */
async function openCharacterPanel() {
  charPanelVisible.value = true
  await nextTick()
  if (mode.value === 'with-char') {
    const desc = (draft.value.main_character_description || draft.value.kor_main_character_description || '').trim()
    if (desc && (!charPromptDirty.value || !charImgPrompt.value.trim())) {
      await fetchCharacterPrompt(false)
    }
  }
}

/* -------------------------
   초안 받아오기 (분기)  ※ 엔드포인트 이름 변경 반영
------------------------- */
const API_GET_CHAR_INFO = '/api/chr_get_scenario_info'
const API_GET_INFO = '/api/get_scenario_info'
const API_GEN_CHAR_PROMPT = '/api/character_image_prompt'
const API_GEN_CHARACTER_IMAGE = '/api/gen_character_image'

async function fetchScenarioDraft() {
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  if (!mode.value) { alert('모드를 선택하세요.'); return }
  const p = user_input.value?.trim()
  if (!p) { alert('주제를 입력하세요.'); return }

  let projectId=store.project_id

  draftLoading.value = true
  draftVisible.value = false
  scenesVisible.value = false
  keyframesVisible.value = false
  charPanelVisible.value = false
  try {
    const url = mode.value === 'with-char' ? API_GET_CHAR_INFO : API_GET_INFO
    const payload = {
      user_id: store.user_id,
      project_id: projectId,
      user_topic_input: p,
      time: Number(durationSec.value)
    }
    const res = await axios.post(url, payload)
    const data = res.data

    if (mode.value === 'with-char') {
      let parsed
      parsed = {
        topic: data.topic ?? '',
        kor_topic: data.kor_topic ?? '',
        description: data.description ?? '',
        kor_description: data.kor_description ?? '',
        main_character: data.main_character ?? '',
        main_character_description: data.main_character_description ?? ''
      }
      draft.value = {
        ...draft.value,
        kor_topic: parsed.kor_topic,
        kor_description: parsed.kor_description,
        main_character: parsed.main_character,
        main_character_description: parsed.main_character_description
      }
      charImgPrompt.value = ''
      charImgUrl.value = ''
      charPromptDirty.value = false
    } 
    else {
      let parsed
      parsed = {
        topic: data.topic ?? '',
        kor_topic: data.kor_topic ?? '',
        description: data.description ?? '',
        kor_description: data.kor_description ?? '',
      }
      draft.value = {
        ...draft.value,
        kor_topic: parsed.kor_topic,
        kor_description: parsed.kor_description,
      }
    }

    draftVisible.value = true
  } catch (e) {
    showError(e, '초안 불러오기 실패')
  } finally {
    draftLoading.value = false
  }
}

/* -------------------------
   with-char: 캐릭터 프롬프트 생성(안전 덮어쓰기)
------------------------- */
async function fetchCharacterPrompt(force = false) {
  if (mode.value !== 'with-char') return
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  const userTopic = user_input.value?.trim()
  const mainCharDesc =
    draft.value.main_character_description?.trim() 
  if (!userTopic) { alert('주제를 먼저 입력하세요.'); return }
  if (!mainCharDesc) { alert('Main Character Description을 입력하세요.'); return }

  if (charPromptLoading.value) return
  charPromptLoading.value = true
  try {
    const projectId = store.project_id
    const res = await axios.post(API_GEN_CHAR_PROMPT, {
      user_id: store.user_id,
      project_id: projectId,
      character_description: mainCharDesc
    })
    const data = res.data
     
    charImgPrompt.value = data?.character_prompt
    charPromptDirty.value = false
      
    
  } catch (e) {
    showError(e, '캐릭터 프롬프트 가져오기 실패')
  } finally {
    charPromptLoading.value = false
  }
}

/* -------------------------
   캐릭터 이미지 생성
------------------------- */
async function generateCharacterImage() {
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  const prompt = (charImgPrompt.value || '').trim()
  if (!prompt) { alert('캐릭터 이미지 프롬프트를 입력하거나 생성하세요.'); return }

  try {
    charImgLoading.value = true
    const projectId = store.project_id

    const payload = {
      user_id: store.user_id,
      project_id: projectId,
      character_prompt: prompt,
      model: charModel.value,
      setup: { width: charWidth.value, height: charHeight.value }
    }

    const res = await axios.post(API_GEN_CHARACTER_IMAGE, payload)
    const url = normalizeImageUrl(res.data?.imageUrl)
    if (url) {
      charImgUrl.value = url
      store.characterImage = {
        url,
        prompt,
        model: charModel.value,
        width: charWidth.value,
        height: charHeight.value
      }
    } 
  } catch (e) {
    showError(e, '캐릭터 이미지 생성 실패')
  } finally {
    charImgLoading.value = false
  }
}

/* -------------------------
   시나리오 생성 (분기) 
------------------------- */
async function generateScenario() {
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }

  if (mode.value === 'with-char') {
    if (!draft.value.main_character?.trim()) { alert('Main Character를 입력하세요.'); return }
    if (!draft.value.main_character_description?.trim()) { alert('Main Character Description을 입력하세요.'); return }
  }

  scenesLoading.value = true
  scenesVisible.value = false
  keyframesVisible.value = false
  try {
    const projectId = store.project_id
    const url = mode.value === 'with-char' ? '/api/chr_gen_contents' : '/api/gen_contents'
    const payload = mode.value === 'with-char' ? {
      character: draft.value.main_character ?? '',
      character_description: draft.value.main_character_description ?? '',
      topic: draft.value.kor_topic,
      description: draft.value.kor_description,
      user_id: store.user_id,
      project_id: projectId
    } : {
      topic: draft.value.kor_topic,
      description: draft.value.kor_description,
      user_id: store.user_id,
      project_id: projectId
    }

    const res = await axios.post(url, payload)
    const data = res.data
    const arr = Array.isArray(data?.kor_contents) ? data.kor_contents : []

    console.log('Generated scenes arr:', arr)

    contents.value = arr
    scenesVisible.value = true
  } catch (e) {
    showError(e, '컷 생성 실패')
  } finally {
    scenesLoading.value = false
  }
}

/* -------------------------
   시나리오 확정 → 키프레임 단계 진입
------------------------- */
async function confirmScenario() {
  finalizing.value = true
  try {
    const projectId = store.project_id

    scenario.value = {
      projectId,
      topic: draft.value.topic,
      description: draft.value.description,
      duration: Number(durationSec.value) || 0,
      main_character: draft.value.main_character ?? '',
      main_character_description: draft.value.main_character_description ?? '',
      contents: contents.value
    }

    store.scenario = scenario.value
    if (charImgUrl.value || charImgPrompt.value) {
      store.characterImage = {
        url: charImgUrl.value,
        prompt: charImgPrompt.value,
        model: charModel.value,
        width: charWidth.value,
        height: charHeight.value
      }
    }

    //scenesVisible.value = false
    //draftVisible.value = false

    // 키프레임 초기화
    keyframePrompts.value = contents.value.map((content, i) => ({
      no: i + 1,
      content,
      prompt: '',
      imageUrl: null,
      imgLoading: false,
      model: 'dalle-3',
      width: 1024,
      height: 1024,
      seriesIndex: 0
    }))
    keyframesVisible.value = true

    await nextTick()
    if (!keyframesLoading.value && keyframePrompts.value.length) {
      await generateAllKeyframePrompts()
    }
  } finally {
    finalizing.value = false
  }
}

/* -------------------------
   키프레임 프롬프트 생성 (배치)
------------------------- */
async function generateAllKeyframePrompts() {
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  if (!contents.value.length) { alert('컷이 없습니다.'); return }
  if (keyframesLoading.value) return

  keyframesLoading.value = true
  try {
    const projectId = store.project_id
    keyframePrompts.value = keyframePrompts.value.map(k => ({ ...k, imgLoading: false }))

    const contents_list = keyframePrompts.value.map(kf => kf.content)
    const res = await axios.post('/api/gen_image_prompt', {
      user_id: store.user_id,
      project_id: projectId,
      contents_list
    })
    const list = Array.isArray(res.data?.image_prompt) ? res.data.image_prompt : []

    keyframePrompts.value = keyframePrompts.value.map((kf, idx) => ({
      ...kf,
      prompt: (list[idx] || '').trim() || kf.prompt
    }))
  } catch (e) {
    console.error(e)
    showError(e, '키프레임 프롬프트 생성 실패')
  } finally {
    keyframesLoading.value = false
  }
}

/* -------------------------
   키프레임 이미지 생성/재생성
------------------------- */
function isPrevCutReady(cutNo) {
  if (cutNo <= 1) return true
  const prev = keyframePrompts.value[cutNo - 2]
  return !!prev?.imageUrl
}

async function generateKeyframeImage(idx) {
  store.imgProgress = 0
  const kf = keyframePrompts.value[idx]; if (!kf) return
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  const prompt = (kf.prompt || '').trim()
  if (!prompt) { alert('프롬프트를 입력하거나 생성하세요.'); return }
  if (kf.no > 1 && !isPrevCutReady(kf.no)) {
    alert('이전 컷 이미지를 먼저 생성하세요.')
    return
  }
  try {
    kf.imgLoading = true
    const projectId = store.project_id
    const image_num = String(kf.no)
    const endpoint = (kf.no === 1) ? '/api/generate_first_image' : '/api/generate_series_image'
    const payload = {
      user_id: store.user_id,
      project_id: projectId,
      prompt,
      model: kf.model,
      block_index: idx,
      setup: { width: kf.width, height: kf.height },
      image_num
    }
    const res = await axios.post(endpoint, payload)
    const url = normalizeImageUrl(res.data?.imageUrl)
    if (url) {
      kf.imageUrl = url
      kf.seriesIndex = (kf.seriesIndex || 0) + 1
    }
  } catch (e) {
    showError(e, '이미지 생성 실패')
  } finally {
    kf.imgLoading = false
  }
}

async function regenKeyframeImage(idx) {
  store.imgProgress = 0
  const kf = keyframePrompts.value[idx]; if (!kf) return
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  if (kf.no > 1 && !isPrevCutReady(kf.no)) {
    alert('이전 컷 이미지를 먼저 생성하세요.')
    return
  }
  const prompt = (kf.prompt || '').trim()
  if (!prompt) { alert('프롬프트를 입력하거나 생성하세요.'); return }
  try {
    kf.imgLoading = true
    const projectId = store.project_id
    const image_num = String(kf.no)
    const endpoint = (kf.no === 1) ? '/api/generate_first_image' : '/api/generate_series_image'
    const payload = {
      user_id: store.user_id,
      project_id: projectId,
      prompt,
      model: kf.model,
      block_index: idx,
      setup: { width: kf.width, height: kf.height },
      image_num
    }
    const res = await axios.post(endpoint, payload)
    const url = normalizeImageUrl(res.data?.imageUrl)
    if (url) {
      kf.imageUrl = url
      kf.seriesIndex = (kf.seriesIndex || 0) + 1
    }
  } catch (e) {
    showError(e, '이미지 재생성 실패')
  } finally {
    kf.imgLoading = false
  }
}

/* -------------------------
   비디오 만들기: 저장 + 다음 페이지 이동 (알림 제거)
------------------------- */
function makeVideo() {
  const clean = keyframePrompts.value.map(k => ({
    no: k.no,
    content: k.content,
    prompt: (k.prompt || '').trim(),
    imageUrl: k.imageUrl || null,
    model: k.model,
    width: k.width,
    height: k.height,
    seriesIndex: k.seriesIndex || 0
  }))
  store.keyframePrompts = clean
  router.push(NEXT_ROUTE)
}

/* -------------------------
   프로젝트
------------------------- */
const groupedProjects = computed(() => {

  const grouped = {}
  const list = Array.isArray(projects.value) ? projects.value : []
  const toDateKey = (p) => {
    const raw = p?.updated_at || p?.created_at || p?.date
    if (!raw) return '미지정'
    const d = new Date(raw)
    if (isNaN(d)) return '미지정'
    const w = ['일','월','화','수','목','금','토'][d.getDay()]
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${yyyy}-${mm}-${dd} (${w})`
  }
  for (const p of list) {
    const key = toDateKey(p)
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(p)
  }
  const sortedKeys = Object.keys(grouped).sort((a, b) => {
    const A = a === '미지정' ? -Infinity : new Date(a.slice(0, 10)).getTime()
    const B = b === '미지정' ? -Infinity : new Date(b.slice(0, 10)).getTime()
    return B - A
  })
  return Object.fromEntries(sortedKeys.map(k => [k, grouped[k]]))
})

async function fetchProjects() {
  draftVisible.value = false
  scenesVisible.value = false
  keyframesVisible.value = false
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  try {
    const projectId = store.project_id
    void projectId
    const res = await axios.get(`/api/projects/${store.user_id}`)
    projects.value = res.data.projects || []
    if (projects.value.length === 0) alert('저장된 프로젝트가 없습니다.')
  } catch (e) {
    showError(e, '프로젝트 목록 불러오기 실패')
  }
}

async function enterProject(projectId) {
  try {
    if (!store.user_id) { alert('로그인이 필요합니다.'); return; }
    const id = Number(projectId);
    if (Number.isNaN(id)) { alert('유효하지 않은 프로젝트 ID입니다.'); return; }

    //화면표시
    draftVisible.value = true
    scenesVisible.value = true
    keyframesVisible.value = true
    
    //데이터 받아오기
    let res
    try {
      res = await axios.get(`/api/project/${store.user_id}/${id}`)
    } catch {
      const userId = store.user_id
      res = await axios.get(`/api/project/${encodeURIComponent(userId)}/${id}`)
    }

    //store.loadProject(res.data);
    draft.value.kor_topic = res.data.title || ''
    draft.value.kor_description = res.data.description || ''
    contents.value=res.data.contents
    keyframePrompts.value=res.data.contents.map((content, i) => ({
      no: i + 1,
      content,
      prompt: res.data.keyframe_prompt[i]??'',
      imageUrl: `/temp/${store.user_id}/${projectId}/keyframe/${i+1}.png`,
      imgLoading: false,
      model: 'dalle-3',
      width: 1024,
      height: 1024,
      seriesIndex: 0
    }))
    user_input.value = res.data.title ?? '';
    if (res.data?.scenario?.info?.timeSec) {
      durationSec.value = Number(res.data.scenario.info.timeSec) || durationSec.value
    }

    store.project_id = id
    console.log('불러온 프로젝트 아이디', store.project_id);
    
  } catch (e) {
    showError(e, '프로젝트 불러오기 실패');
  }
}

/* -------------------------
   라우팅
------------------------- */
async function goNext() {
  // 1) 현재 키프레임/시나리오를 확정 저장
  const clean = (keyframePrompts.value || []).map(k => ({
    no: k.no,
    content: k.content,
    prompt: (k.prompt || '').trim(),
    imageUrl: k.imageUrl || null,
    model: k.model,
    width: k.width,
    height: k.height,
    seriesIndex: k.seriesIndex || 0
  }))
  store.keyframePrompts = clean
  store.scenario = scenario.value
  sessionStorage.setItem('keyframePrompts', JSON.stringify(clean))
  sessionStorage.setItem('scenario', JSON.stringify(scenario.value || {}))
  sessionStorage.setItem('project_id', String(store.project_id || ''))

  // 2) 반영 완료 대기 후 이동(초진입 흰 화면 방지)
  await nextTick()
  await router.push({ path: '/keyframes', query: { v: Date.now().toString() } }) // v 쿼리로 강제 리마운트
}

</script>
