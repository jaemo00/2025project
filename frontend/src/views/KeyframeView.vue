<template>
  <div class="min-h-screen flex flex-col items-center bg-[#12100E] px-4 md:px-8 xl:px-12 py-10 text-gray-100">
    <div class="bg-[#1A1816] rounded-xl shadow-xl p-6 w-full max-w-6xl xl:max-w-7xl 2xl:max-w-[90rem] border border-[#FFB224]/20">
      <h1 class="text-2xl font-bold text-[#FFB224] text-center mb-6">비디오 생성</h1>

      <!-- 상단: 좌(비디오 프롬프트) / 우(키프레임 카드 3장씩) -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 좌측: 비디오 프롬프트 -->
        <section class="bg-[#12100E]/60 rounded-lg border border-[#FFB224]/20 p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-semibold text-[#FFB224]">
              컷 {{ activeCard + 1 }} · 비디오 프롬프트
            </h2>
            <button
              class="px-3 py-1.5 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 hover:bg-[#FFB224]/10"
              :disabled="promptLoading"
              @click="fetchVideoPrompt"
            >
              <span v-if="promptLoading">프롬프트 생성 중…</span>
              <span v-else>프롬프트 다시받기</span>
            </button>
          </div>

          <div class="space-y-3">
            <div>
              <label class="text-xs text-gray-400 block mb-1">Korean (읽기전용)</label>
              <textarea
                v-model="videoPromptKor"
                readonly
                rows="6"
                class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-200 placeholder-gray-500 border border-[#FFB224]/30"
              ></textarea>
            </div>

            <div>
              <label class="text-xs text-gray-400 block mb-1">English (편집 가능 · 비디오 생성에 사용)</label>
              <textarea
                v-model="videoPromptEng"
                :disabled="promptLoading || videoLoading"
                rows="8"
                class="w-full p-3 rounded-md resize-y bg-[#12100E] text-gray-100 placeholder-gray-500 border border-[#FFB224]/30 focus:outline-none focus:ring-2 focus:ring-[#FFB224]"
                placeholder="Edit only the English part here. This will be used for video generation."
              ></textarea>
            </div>

            <div class="flex justify-end">
              <button
                class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E] hover:bg-[#e6a020] disabled:opacity-50"
                :disabled="!canGenerateVideo || videoLoading"
                @click="generateVideo"
              >
                <span v-if="videoLoading">비디오 생성 중…</span>
                <span v-else>비디오 생성하기</span>
              </button>
            </div>
          </div>
        </section>

        <!-- 우측: 3장씩 슬라이딩 윈도우 카드 -->
        <section class="bg-[#12100E]/60 rounded-lg border border-[#FFB224]/20 p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(card, i) in imageCards"
              :key="i"
              class="border rounded-lg p-3 cursor-pointer transition"
              :class="i === activeCard ? 'border-[#FFB224] ring-1 ring-[#FFB224]/60' : 'border-[#FFB224]/20 hover:border-[#FFB224]/40'"
              @click="activeCard = i"
            >
              <div class="text-sm font-semibold text-[#FFB224] mb-2">컷 {{ i + 1 }}</div>
              <div class="grid grid-cols-3 gap-2">
                <div v-for="(img, j) in card.images" :key="j" class="flex flex-col gap-1">
                  <div class="text-[11px] text-gray-400 text-center">
                    {{ ['시작 키프레임','중간 키프레임','마지막 키프레임'][j] }}
                  </div>
                  <div class="aspect-square border border-[#FFB224]/30 rounded overflow-hidden bg-[#0E0D0B] flex items-center justify-center">
                    <img
                      v-if="img"
                      :src="img"
                      class="w-full h-full object-cover"
                      :alt="`card-${i}-img-${j}`"
                    />
                    <span v-else class="text-[11px] text-gray-500">이미지 없음</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="!imageCards.length" class="text-sm text-gray-400 col-span-full">
              3장 이상 생성된 키프레임 이미지가 있어야 카드가 보입니다.
            </div>
          </div>
        </section>
      </div>

      <!-- 하단: 생성된 비디오 + 버튼 -->
      <section class="bg-[#12100E]/60 rounded-lg border border-[#FFB224]/20 p-5 mt-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
          <div class="border border-[#FFB224]/20 rounded p-3">
            <div class="text-sm text-gray-300 mb-2">생성 영상</div>
            <div class="aspect-video bg-black/60 rounded flex items-center justify-center">
              <video
                v-if="currentVideoUrl"
                :src="currentVideoUrl"
                class="w-full h-full"
                controls
              ></video>
              <div v-else class="text-sm text-gray-500">아직 생성된 영상이 없습니다.</div>
            </div>

            <!-- ✅ 진행률 바 -->
            <div
              v-if="videoLoading || (videoProgress > 0 && videoProgress < 100)"
              class="mt-4"
            >
              <div class="flex justify-between text-xs text-gray-400 mb-1">
                <span>비디오 생성 진행률</span>
                <span>{{ videoProgress }}%</span>
              </div>
              <div class="w-full h-2 bg-gray-800 rounded overflow-hidden">
                <div
                  class="h-2 bg-[#FFB224] transition-all"
                  :style="{ width: videoProgress + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <div class="flex flex-col gap-3">
            <button
              class="px-4 py-2 rounded font-semibold bg-transparent text-[#FFB224] border border-[#FFB224]/60 hover:bg-[#FFB224]/10"
              :disabled="videoLoading || !String(videoPromptEng || '').trim()"
              @click="generateVideo"
            >
              재생성
            </button>
            <button
              class="px-4 py-2 rounded font-semibold bg-[#FFB224] text-[#12100E] hover:bg-[#e6a020]"
              @click="combine"
            >
              최종영상생성
            </button>
          </div>
        </div>
      </section>

      <!-- 최종생성영상 -->
    <section
      v-if="final_video_url"
      class="mt-8 bg-[#12100E]/60 rounded-lg border border-[#FFB224]/20 p-5"
      >
      <h2 class="text-lg font-semibold text-[#FFB224] mb-3">
        최종 생성 영상
      </h2>
      <div class="aspect-video bg-black/60 rounded flex items-center justify-center">
        <video :src="final_video_url" class="w-full h-full" controls></video>
      </div>
    </section>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/appStore'
import axios from 'axios'

/** 라우팅 */
const router = useRouter()
const store = useAppStore()

/** 상태 */
const promptLoading = ref(false)
const videoLoading  = ref(false)

/** 다중 카드(윈도우) 프롬프트 상태 */
const activeCard = ref(0)
const videoPromptKorList = ref([]) // string[]
const videoPromptEngList = ref([]) // string[]

/** 현재 카드의 v-model용 computed (문자열 보장) */
const videoPromptKor = computed({
  get: () => String(videoPromptKorList.value[activeCard.value] ?? ''),
  set: v   => videoPromptKorList.value[activeCard.value] = String(v ?? '')
})
const videoPromptEng = computed({
  get: () => String(videoPromptEngList.value[activeCard.value] ?? ''),
  set: v   => videoPromptEngList.value[activeCard.value] = String(v ?? '')
})

const videoUrls = ref([])
const final_video_url=ref('')


const videoProgress = computed(() => Number(store.videoProgress || 0))
const currentVideoUrl = computed(() =>
  String(videoUrls.value[activeCard.value] || '')
)

/** 유틸: 이미지 경로 정규화 */
function normalizeUrl(p) {
  if (!p) return ''
  let s = String(p).replaceAll('\\', '/')
  if (/^https?:|^data:/.test(s)) return s
  if (s.includes('/temp/')) s = s.slice(s.indexOf('/temp/'))
  if (!s.startsWith('/')) s = '/' + s
  return s
}

/** project_id 확보 */
async function getProjectIdOrThrow(titleForCreate = 'Untitled') {
  let pid = Number(
    (store.project_id ?? null) ??
    (store.scenario?.projectId ?? null) ??
    (sessionStorage.getItem('project_id') ?? null)
  )
  if (!Number.isInteger(pid) || pid <= 0) {
    const res = await axios.post('/api/project', { user_id: store.user_id, title: titleForCreate })
    pid = Number(res.data?.project_id ?? res.data?.id)
  }
  if (!Number.isInteger(pid) || pid <= 0) throw new Error('project_id 확보 실패')
  store.project_id = pid
  sessionStorage.setItem('project_id', String(pid))
  return pid
}

/** 모드 추론: 스토어 저장값 우선, 없으면 캐릭터 이미지 존재 여부로 추정 */
const mode = computed(() => store.mode || (store.characterImage ? 'with-char' : 'no-char'))

/** 윈도우(3장씩, stride=2) 계산: [1,2,3], [3,4,5], ... */
const windows = computed(() => {
  const cuts = (store.keyframePrompts || []).filter(k => k?.imageUrl)
  const W = 3, stride = 2
  const list = []
  for (let i = 0; i + W <= cuts.length; i += stride) {
    const a = cuts[i]?.no, b = cuts[i + 1]?.no, c = cuts[i + 2]?.no
    if (a && b && c) list.push({ start: a, mid: b, end: c })
  }
  return list
})

/** 카드(프리뷰용 이미지 3개씩) */
const imageCards = computed(() => {
  const cuts = (store.keyframePrompts || []).filter(k => k?.imageUrl).map(k => normalizeUrl(k.imageUrl))
  const res = []
  const W = 3, stride = 2
  for (let i = 0; i + W <= cuts.length; i += stride) {
    const triplet = cuts.slice(i, i + W)
    if (triplet.length === 3 && triplet.every(Boolean)) {
      res.push({ images: [triplet[0], triplet[1], triplet[2]] })
    }
  }
  return res
})

/** 비디오 생성 가능 여부 (현재 카드 기준) */
const canGenerateVideo = computed(() =>
  !!store.user_id &&
  !!store.project_id &&
  !!String(videoPromptEng.value || '').trim() &&
  windows.value.length > 0
)

/** 비디오 프롬프트 호출 (모드별) — 배열 응답 대응 */
async function fetchVideoPrompt() {
  if (!store.user_id) { alert('로그인이 필요합니다.'); return }
  promptLoading.value = true
  try {
    const pid = store.project_id
    const url = mode.value === 'with-char'
      ? '/api/chr_gen_video_prompt'
      : '/api/gen_video_prompt'

    // 보통 서버는 user_id, project_id만으로 DB에서 조회 가능
    const res = await axios.post(url, { user_id: store.user_id, project_id: pid })
    const data = res.data || {}

    // 기대 형식: { video_prompt: string[], kor_video_prompt: string[] }
    let engArr = []
    let korArr = []

    if (Array.isArray(data.video_prompt)) engArr = data.video_prompt.map(x => String(x ?? ''))
    if (Array.isArray(data.kor_video_prompt)) korArr = data.kor_video_prompt.map(x => String(x ?? ''))

    // 백업: 다른 키로 올 수 있음
    if (!engArr.length && Array.isArray(data.eng_video_prompt)) engArr = data.eng_video_prompt.map(x => String(x ?? ''))
    if (!korArr.length && Array.isArray(data.kor)) korArr = data.kor.map(x => String(x ?? ''))

    // 문자열 하나만 오는 경우를 대비해 배열로 승격
    const asArray = v => (v ? [String(v)] : [])
    if (!engArr.length && typeof data.video_prompt === 'string') engArr = asArray(data.video_prompt)
    if (!korArr.length && typeof data.kor_video_prompt === 'string') korArr = asArray(data.kor_video_prompt)

    // 윈도우 개수와 길이 맞추기
    const n = Math.max(1, windows.value.length)
    const ensureLen = (arr, len) => {
      if (arr.length === len) return arr
      if (arr.length === 1) return Array(len).fill(arr[0])
      return Array.from({ length: len }, (_, i) => String(arr[i] ?? ''))
    }

    videoPromptEngList.value = ensureLen(engArr, n)
    videoPromptKorList.value = ensureLen(korArr, n)
    activeCard.value = 0
  } catch (e) {
    console.error(e)
    alert('비디오 프롬프트 가져오기에 실패했습니다.')
  } finally {
    promptLoading.value = false
  }
}

/** 비디오 생성 — 현재 카드만 생성, 응답의 video_dir 지원 */
async function generateVideo() {
  if (!canGenerateVideo.value) return
  videoLoading.value = true
  store.videoProgress = 0
  try {
    const pid = store.project_id
    const w = windows.value[activeCard.value]
    if (!w) throw new Error('윈도우가 없습니다.')

    const cardIndex = activeCard.value
    // 시작 컷의 해상도로 사용(없으면 기본)
    const width  =  720
    const height =  720

    // 프레임/초 계산(카드 수 기준으로 대략 분할)
    const fps = 16
    const num_frame = 77

    const payload = {
      user_id: store.user_id,
      project_id: pid,
      prompt: String(videoPromptEng.value || '').trim(), // 백엔드가 prompt로 받음
      height, width, num_frame, fps,
      cut_num: String(activeCard.value + 1)
    }

    const res = await axios.post('/api/gen_video', payload)
    const url = normalizeUrl(res.data?.video_dir || res.data?.videoUrl || res.data?.url)
    if (url) {
      // 기존: videoUrls.value = url   ❌
      const next = [...videoUrls.value]   // 기존 배열 복사
      next[cardIndex] = url               // 카드 인덱스 위치에 저장
      videoUrls.value = next              // 새 배열로 교체(반응성 유지)

      if (!store.video) store.video = {}
      store.video[cardIndex + 1] = {
        url,
        prompt_eng: String(videoPromptEng.value || '').trim(),
        cut_num: cardIndex + 1
      }
    }
  } catch (e) {
    console.error(e)
    alert('비디오 생성에 실패했습니다.')
  } finally {
    videoLoading.value = false
  }
}

/** 확정 → 다음 단계(필요한 경로로 변경 가능) */
async function combine() {
  const res=await axios.post('/api/combine',{ user_id: store.user_id, project_id: store.project_id })
  final_video_url.value=normalizeUrl(res.data.final_video)

}

/** 초기 진입 가드 & 프롬프트 선호출 */
onMounted(async () => {
  if (!store.user_id) {
    alert('로그인이 필요합니다.')
    router.push('/')
    return
  }

  if (!store.socket) {
    store.connectWebSocket()
  }

  if (!store.scenario || !(store.keyframePrompts || []).some(k => k?.imageUrl)) {
    console.warn('scenario or keyframe images missing')
  }
  await fetchVideoPrompt()

  
})
</script>

<style scoped>
.aspect-square { position: relative; width: 100%; padding-top: 100%; }
.aspect-square > * { position: absolute; top:0; left:0; right:0; bottom:0; }
.aspect-video { position: relative; width: 100%; padding-top: 56.25%; }
.aspect-video > * { position: absolute; top:0; left:0; right:0; bottom:0; }
</style>
