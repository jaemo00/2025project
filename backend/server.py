import torch
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
from diffusers import DiffusionPipeline
from diffusers import StableDiffusionPipeline
from diffusers import I2VGenXLPipeline
from diffusers.utils import export_to_gif, load_image
import shutil
'''
#이미지 모델
pipe = StableDiffusionPipeline.from_single_file(
    "C:/Users/AhnLab/Desktop/DreamShaper_8.safetensors",  # DreamShaper 파일 경로
    torch_dtype=torch.float16,
    safety_checker=None,  # 필요 시 꺼줄 수 있음
)
pipe = pipe.to("cuda")
print(torch.cuda.is_available())

generator = torch.manual_seed(33)

#영상 모델
pipeline = I2VGenXLPipeline.from_pretrained("ali-vilab/i2vgen-xl", torch_dtype=torch.float16, variant="fp16")
pipeline.enable_model_cpu_offload()
'''

#데이터 파싱
class ImageRequest(BaseModel):
    user_id: str
    prompt: str

class VideoRequest(BaseModel):
    user_id: str
    imagePrompt: str
    videoPrompt: str
    

#pipe.load_lora_weights("C:/Users/AhnLab/Desktop/sd1.5.safetensors",weight_name="default", lora_scale=0.7) #0.5~1

import mimetypes
# .js 파일에 대해 MIME 타입 명시적으로 추가
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = FastAPI()
#BASE_DIR = pathlib.Path(__file__).parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")  # frontend 폴더 위치
DIST_DIR = os.path.join(FRONTEND_DIR, "dist") 
ASSETS_DIR = os.path.join(DIST_DIR, "assets")
 
#웹소켓 등록을 먼저해야함
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # URL 쿼리 파라미터로 user_id 받아오기
    user_id = websocket.query_params.get("user_id")
    print(f"{user_id}")

    try:
        while True:
            data = await websocket.receive_text()
            # 필요하면 처리
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")
        # 사용자 temp폴더 삭제
        user_temp_folder = os.path.join(TEMP_DIR, user_id)
        if os.path.exists(user_temp_folder):
            shutil.rmtree(user_temp_folder)

@app.get('/',response_class=HTMLResponse)
async def serve_frontend():
    with open(os.path.join(DIST_DIR, "index.html"), encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

# frontend 폴더 mount
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
app.mount(
    "/assets",
    StaticFiles(directory=ASSETS_DIR),  
    name="assets"
)
# static 파일들 mount
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")




#fallback함수 : vue에서 처리할 경로의 요청은 index.html 보냄
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def fallback(full_path: str):
    if full_path.startswith("ws"):
        return HTMLResponse(status_code=404, content="웹소켓은 FastAPI가 처리함")
    return FileResponse(os.path.join(DIST_DIR, "index.html"))


@app.post("/api/generate-image")
async def generate_image(data: ImageRequest):

    """클라이언트에서 JSON 데이터를 받아 응답하는 핸들러"""
    try:
        user_id = data.user_id
        text = data.prompt
        #image = pipe(text, generator=generator, num_inference_steps=30).images[0]

        image_filename=text+'.png'

        #사용자 전용 폴더생성
        user_folder = os.path.join(TEMP_DIR, user_id)
        os.makedirs(user_folder, exist_ok=True)
        
        image_path = os.path.abspath(os.path.join(user_folder, image_filename))
        #image.save(image_path)
        
        print(f"Received text: {image_filename}") 

        if not os.path.exists(image_path):
            image_path = os.path.join(TEMP_DIR, "default.png")  # 기본 이미지 반환
        print(f"path:{image_path}")
        return JSONResponse(content={"imageUrl": image_filename,"status":"success"})
        

    except Exception as e:
        return JSONResponse(content={"imageUrl": image_filename,"status":"success"})
    


@app.post("/api/generate-video")
async def generate_video(data: VideoRequest):

    """클라이언트에서 JSON 데이터를 받아 응답하는 핸들러"""
    try:
        user_id = data.user_id
        image_filename=data.imagePrompt+'.png'
        user_folder = os.path.join(TEMP_DIR, user_id)
        image_path = os.path.abspath(os.path.join(user_folder, image_filename))
        #image = load_image(image_path).convert("RGB")
            
        print(f"Received imagefile: {image_filename}") 
        '''
        frames = pipeline(
            prompt=data.videoPrompt,
            image=image,
            num_inference_steps=40,
            negative_prompt="",
            guidance_scale=1,
            generator=generator
        ).frames[0]
        '''
        video_filename=data.imagePrompt+'.gif'
        '''
        video_path = os.path.abspath(os.path.join(user_folder, video_filename))
        export_to_gif(frames, video_path)'''
        return JSONResponse(content={"videoUrl": video_filename,"status":"success"})
    except Exception as e:
        return JSONResponse(content={"videoUrl": video_filename,"status":"success"})

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
