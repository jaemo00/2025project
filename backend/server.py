import torch
import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends,APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import json
import os
import re
from PIL import Image
from typing import Dict, Optional, List
from diffusers import DiffusionPipeline
from diffusers import StableDiffusionPipeline
from diffusers import I2VGenXLPipeline
from diffusers.utils import export_to_gif, load_image
import shutil
from langchain import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging, traceback
from pathlib import Path

from api import api_scenario
from config import *

from sqlalchemy.orm import Session
import models
from database import engine, Base, SessionLocal
from fastapi.exceptions import RequestValidationError



#pip install fastapi uvicorn pydantic langchain langchain-openai langchain-core openai \
#diffusers transformers accelerate safetensors Pillow torch python-dotenv sqlalchemy

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)


#데이터 파싱
class init(BaseModel):
    user_id: str




class VideoRequest(BaseModel):
    user_id: str
    imagePrompt: str
    videoPrompt: str
    block_index: Optional[int] = 0  # block_index 추가

class VideoBetweenRequest(BaseModel):
    user_id: str
    startImage: str
    endImage: str
    prompt: str
    width: int
    height: int
    totalFrames: int
    fps: int
    block_index: Optional[int] = 0
    


class ScenarioResponse(BaseModel):
    status: str
    scenario: str
    projectId: int 



import mimetypes
# .js 파일에 대해 MIME 타입 명시적으로 추가
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

app = FastAPI()

app.include_router(api_scenario.router)



# 전역 변수로 WebSocket 연결 저장
active_websockets = {}

# 진행률 전송 함수
async def send_progress(user_id: str, block_index: int, progress: int):
    if user_id in active_websockets:
        try:
            websocket = active_websockets[user_id]
            await websocket.send_json({
                "type": "image_progress",
                "blockIndex": block_index, 
                "progress": progress
            })
            print(f"📊 진행률 전송: Block {block_index} - {progress}%")
        except:
            if user_id in active_websockets:
                del active_websockets[user_id]
                print(f"❌ WebSocket 연결 제거: {user_id}")

async def send_video_progress(user_id: str, block_index: int, progress: int):
    if user_id in active_websockets:
        try:
            websocket = active_websockets[user_id]
            await websocket.send_json({
                "type": "video_progress",
                "blockIndex": block_index, 
                "progress": progress
            })

        except:
            if user_id in active_websockets:
                del active_websockets[user_id]


# 예외 디버깅 함수
logger = logging.getLogger("app")
def dump_exc(prefix: str, e: Exception):
    tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
    logger.error("%s: %s\n%s", prefix, repr(e), tb)

#웹소켓 등록을 먼저해야함
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = websocket.query_params.get("user_id")
    
    # 사용자별 WebSocket 연결 저장
    active_websockets[user_id] = websocket
    print(f"✅ WebSocket 연결됨: {user_id}")
    
    try:
        while True:
            # 연결 유지를 위해 메시지 대기
            data = await websocket.receive_text()
            print(f"📨 받은 메시지: {data}")
    except WebSocketDisconnect:
        # 연결 해제 시 제거
        if user_id in active_websockets:
            del active_websockets[user_id]
        print(f"❌ WebSocket 연결 해제: {user_id}")

# frontend 폴더 mount
# app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
# app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets"
# )
# # static 파일들 mount
# app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

# 1.1 주제생성

    


@app.post("/api/generate-video")
async def generate_video(data: VideoRequest):
    """클라이언트에서 JSON 데이터를 받아 응답하는 핸들러"""
    video_filename = data.imagePrompt + '.gif'
    block_index = data.block_index
    
    try:
        user_id = data.user_id
        image_filename = data.imagePrompt + '.png'
        user_folder = os.path.join(TEMP_DIR, user_id)
        image_path = os.path.abspath(os.path.join(user_folder, image_filename))
        
        # 비디오 생성 시작 - 진행률 0%
        await send_video_progress(data.user_id, block_index, 0)
        
        image = load_image(image_path).convert("RGB")
        generator = torch.manual_seed(33)
            
        print(f"📁 Received imagefile: {image_filename}") 
        
        # 비디오 생성 과정의 단계별 진행률
        total_steps = 40  # inference steps
        
        # 비디오 콜백 함수 (비디오 파이프라인도 유사하게 작동)
        def video_step_callback(pipe, step_index, timestep, callback_kwargs):
            current_step = step_index + 1
            progress = int(current_step / total_steps * 100)
            
            print(f"🎬 Video Step {current_step}/{total_steps} ({progress}%)")
            
            # 비동기 작업을 이벤트 루프에 추가
            loop = asyncio.get_event_loop()
            loop.create_task(send_video_progress(data.user_id, block_index, progress))
            
            return callback_kwargs
        
 
        
        # 비디오 파일 저장 (주석 해제하면 실제 저장됨)
        # video_path = os.path.abspath(os.path.join(user_folder, video_filename))
        # export_to_gif(frames, video_path)
        
        print(f"✅ 비디오 생성 완료: {video_filename}")
        return JSONResponse(content={
            "videoUrl": video_filename,
            "status": "success"
        })
        
    except Exception as e:
        print(f"❌ 비디오 생성 실패: {e}")
        return JSONResponse(content={
            "videoUrl": video_filename,
            "status": "fail",
            "error": str(e)
        }, status_code=500)
    





 

@app.post('/api/init-user')
def init(user_id:init):
    user_folder = TEMP_DIR / user_id.user_id
    user_folder.mkdir(parents=True,exist_ok=True)
    print(f"사용자 폴더 생성: {user_id}")

@app.post('/api/init-user')
def init(user_id:init):
    user_folder = os.path.join(TEMP_DIR, user_id.userid)
    os.makedirs(user_folder, exist_ok=True)
    print(f"{user_id}")

@app.get("/api/saved/{user_id}")
def get_user_texts(user_id: str, db: Session = Depends(get_db)):
    print("사용자 데이터 조회 실행")
    scenario = db.query(models.Scenario).filter(models.Scenario.user_id == user_id).all()
    image = db.query(models.Image).filter(models.Image.user_id==user_id).all()

    data_scenario = [{"id": item.id, "Scenario": item.content} for item in scenario]
    data_image = [{"id":item.id,"image":item.prompt,"model":item.model,"width":item.width,"height":item.height} for item in image]

    return JSONResponse(content={"user_id": user_id, "Scenario": data_scenario, "image":data_image})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("🔎 Validation error detail:", exc.errors())   # 콘솔에 상세 출력
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# @app.get('/',response_class=HTMLResponse)
# async def serve_frontend():
#     print("메인 페이지 실행")
#     with open(os.path.join(DIST_DIR, "index.html"), encoding="utf-8") as f:
#         html = f.read()
#     return HTMLResponse(content=html)

@app.get("/api/projects/{user_id}")
def get_user_projects(user_id: str, db: Session = Depends(get_db)):
    """사용자의 프로젝트 목록을 반환"""
    try:
        print(f"📋 사용자 프로젝트 목록 조회: {user_id}")
        
        # 특정 컬럼만 선택해서 조회 (created_at, updated_at 제외)
        projects = db.query(
            models.Project.id,
            models.Project.user_id,
            models.Project.title
        ).filter(
            models.Project.user_id == user_id
        ).order_by(models.Project.id.desc()).all()
        
        project_list = []
        for project in projects:
            try:
                project_list.append({
                    "projectId": project.id,
                    "title": project.title or "제목 없음",
                    "date": "최근"  # 임시로 고정값 사용
                })
            except Exception as e:
                print(f"❌ 프로젝트 처리 중 오류: {e}")
                continue
        
        print(f"✅ 총 {len(project_list)}개 프로젝트 조회됨")
        
        return JSONResponse(content={
            "user_id": user_id,
            "projects": project_list
        })
        
    except Exception as e:
        print(f"❌ 프로젝트 목록 조회 실패: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(content={
            "user_id": user_id,
            "projects": [],
            "error": str(e)
        }, status_code=500)
    

@app.get("/api/project/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    # 프로젝트 기본 정보
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 시나리오 1개 가져오기
    scenario = db.query(models.Scenario).filter(models.Scenario.project_id == project_id).first()
    scenario_text = scenario.content if scenario else ""

    # 이미지/비디오 가져오기
    images = db.query(models.Image).filter(models.Image.project_id == project_id).all()
    keyframes = []
    for img in images:
        keyframes.append({
            "prompt": img.prompt,
            "imageUrl": img.image_path,  # 저장된 경로 사용
            "actionPrompt": getattr(img, "action_prompt", ""),
            "videoUrl": getattr(img, "video_path", "")
        })

    return {
        "projectId": project.id,
        "title": project.title,
        "scenario": scenario_text,
        "keyframes": keyframes
    }

#fallback함수 : vue에서 처리할 경로의 요청은 index.html 보냄
# @app.get("/{full_path:path}", response_class=HTMLResponse)
# async def fallback(full_path: str):
#     print("🔄 폴백함수 실행")
#     if full_path.startswith("ws"):
#         return HTMLResponse(status_code=404, content="웹소켓은 FastAPI가 처리함")
#     return FileResponse(os.path.join(DIST_DIR, "index.html"))
@app.get("/")
async def root():
    return {"message": "Hello Backend"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)