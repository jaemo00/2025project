<template>
    <div>
      <ScenarioSection />
      <ArrowNextButton target="/keyframes" />
    </div>
  </template>
  
  <script>
  import ScenarioSection from '@/components/ScenarioSection.vue';
  import ArrowNextButton from '@/components/ArrowNextButton.vue';
  
  export default {
    components: {
      ScenarioSection,
      ArrowNextButton,
    },
    data() {
      return {
        userId: null,
       socket: null
      };
    },
    mounted() {
    // UUID 생성
      this.userId = crypto.randomUUID();
      console.log("생성된 사용자 ID:", this.userId);

     // 웹소켓 연결하면서 id전달
      this.socket = new WebSocket(`ws://localhost:8000/ws?user_id=${this.userId}`);

     this.socket.onopen = (event) => {
      console.log("웹소켓 연결 성공");
      };

      this.socket.onclose = (event) => {
        console.log("웹소켓 연결 종료");
     };

      this.socket.onerror = (error) => {
       console.error("웹소켓 에러 발생:", error);
     };

      this.socket.onmessage = (event) => {
       console.log("서버로부터 받은 메시지:", event.data);
      };
    }
  };
  </script>