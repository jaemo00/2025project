import cv2
import time
from pathlib import Path

def get_last_frame(video_path:str,save_path:str, i:int):
        saved_path = Path(save_path) / f"{i}_start.png" # ← 저장할 이미지 경로
        #save_path = os.path.expanduser("~/last_frame.jpg")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("❌ 영상 파일을 열 수 없습니다.")

        # 마지막 프레임 추출
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)

        # 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            raise Exception("❌ 마지막 프레임을 읽을 수 없습니다.")

        # 이미지 저장
        cv2.imwrite(str(saved_path), frame)

        prev_size = -1
        for _ in range(40):  # 최대 10초 대기 (0.5s * 20)
            if saved_path.exists():
                size = saved_path.stat().st_size
                if size > 0 and size == prev_size:
                    break
                prev_size = size
            time.sleep(0.5)

        print("✅ 마지막 프레임 저장 확인됨, 다음 단계 실행")
        # 자원 해제
        cap.release()
        return saved_path