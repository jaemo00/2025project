import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,garbage_collection_threshold:0.8,max_split_size_mb:64"

import torch
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends,APIRouter, Form, File, UploadFile, Request
from fastapi.responses import JSONResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from PIL import Image
from typing import Dict, Optional, List
from diffusers import DiffusionPipeline
from diffusers import AutoencoderKLWan, WanVACEPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
import shutil
from langchain import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import logging, traceback
from pathlib import Path
import anyio, gc

from api import api_video
from api import api_scenario
from api import api_image
from api import api_chr_scenario
from api import api_chr_image
from utils.config import *
import utils.scenario as scenario
from app_core import app

from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import engine, Base, SessionLocal
from fastapi.exceptions import RequestValidationError


load_dotenv()
#pip install fastapi uvicorn pydantic langchain langchain-openai langchain-core openai \
#diffusers transformers accelerate safetensors Pillow torch python-dotenv sqlalchemy
# pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
# pipe.vae.enable_tiling()
# pipe.vae.enable_slicing()
# pipe.to("cuda")
app.state.pipe = None
app.state.video_pipe=None
app.state.EMIT_LOOP=None
app.state.gpu_sem = anyio.Semaphore(1)  # 동시 생성 제한
app.state.active_websockets = {}

def load_pipe():
    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    pipe.to("cuda")

    return pipe

def load_video_pipe():
    model_id = "Wan-AI/Wan2.1-VACE-1.3B-diffusers"
    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanVACEPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
    flow_shift = 5.0  # 480p면 3.0, 720p면 5.0 권장
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=flow_shift)
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    pipe.to("cuda")

    return pipe

def unload_pipe_fully(pipe) -> None:
    try:
        # pipe.to("cpu")를 추가로 넣어도 되지만 '완전 해제' 목적이면 생략 가능
        pass
    finally:
        del pipe
        gc.collect()
        torch.cuda.empty_cache()


@app.on_event("startup")
async def init_once():
    if app.state.EMIT_LOOP is None:
        app.state.EMIT_LOOP = asyncio.get_running_loop()

    app.state.model_lock = asyncio.Lock()
    app.state.pipe = None
    app.state.video_pipe = None



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
    project_id:int
    imagePrompt: str
    videoPrompt: str


import mimetypes
# .js 파일에 대해 MIME 타입 명시적으로 추가
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')



app.include_router(api_scenario.router)
app.include_router(api_image.router)
app.include_router(api_video.router)
app.include_router(api_chr_scenario.router)
app.include_router(api_chr_image.router)






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
    app.state.active_websockets[user_id] = websocket
    print(f"✅ WebSocket 연결됨: {user_id}")
    
    try:
        while True:
            # 연결 유지를 위해 메시지 대기
            data = await websocket.receive_text()
            print(f"📨 받은 메시지: {data}")
    except WebSocketDisconnect:
        # 연결 해제 시 제거
        if user_id in app.state.active_websockets:
            del app.state.active_websockets[user_id]
        print(f"❌ WebSocket 연결 해제: {user_id}")

#frontend 폴더 mount
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets"
)
# static 파일들 mount
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")





@app.post('/api/init-user')
def init(user_id:init):
    user_folder = TEMP_DIR / user_id.user_id
    user_folder.mkdir(parents=True,exist_ok=True) 

    # base_dir 안의 하위 폴더 중 숫자로 된 것만 추출
    num_folders = [int(p.name) for p in user_folder.iterdir() if p.is_dir() and p.name.isdigit()]

    if not num_folders:
        project_id=1
    else:
        project_id = max(num_folders)+1
    return JSONResponse(content={
            "project_id": project_id
        })
    
    





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

@app.get('/',response_class=HTMLResponse)
async def serve_frontend():
    print("메인 페이지 실행")
    with open(os.path.join(DIST_DIR, "index.html"), encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.get("/api/projects/{user_id}")
def get_user_projects(user_id: str, db: Session = Depends(get_db)):
    """사용자의 프로젝트 목록을 반환"""
    try:
        print(f"📋 사용자 프로젝트 목록 조회: {user_id}")
        
        # 특정 컬럼만 선택해서 조회 (created_at, updated_at 제외)
        projects = db.query(
            models.Scenario
        ).filter(
            models.Scenario.user_id == user_id
        ).order_by(models.Scenario.id.desc()).all()
        
        project_list = []
        for project in projects:
            try:
                project_list.append({
                    "project_id": project.project_id,
                    "title": project.user_topic_input or "제목 없음",
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
    

@app.get("/api/project/{user_id}/{project_id}")
def get_project(user_id:str,project_id: int, db: Session = Depends(get_db)):
    # 프로젝트 기본 정보
    scenario_db = (
    db.query(models.Scenario)
      .filter(
          models.Scenario.user_id == user_id,
          models.Scenario.project_id == project_id,
      )
      .order_by(models.Scenario.id.desc())
      .first())
    
    if not scenario_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # 이미지/비디오 가져오기
    image_db = (
    db.query(models.Image)
      .filter(
          models.Image.user_id == user_id,
          models.Image.project_id == project_id,
      ).first())
    
    kor_contents=scenario.split_contents(scenario.translate_eng2kor(scenario_db.contents))
    print(scenario_db.contents)
    print(kor_contents)
    return {
        "title": scenario_db.user_topic_input,
        "topic": scenario.translate_eng2kor(scenario_db.topic),
        "description" : scenario.translate_eng2kor(scenario_db.description),
        "contents":kor_contents,
        "keyframe_prompt": image_db.image_prompt,
        "video_prompt" : image_db.video_prompt
    }

#fallback함수 : vue에서 처리할 경로의 요청은 index.html 보냄
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def fallback(full_path: str):
    print("🔄 폴백함수 실행")
    if full_path.startswith("ws"):
        return HTMLResponse(status_code=404, content="웹소켓은 FastAPI가 처리함")
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
# @app.get("/")
# async def root():
#     return {"message": "Hello Backend"}

if __name__ == "__main__":
    uvicorn.run(
        "server:app",          # 모듈:변수
        host="0.0.0.0",        # 외부 접속 허용
        port=8080,             # 포트 번호
        reload=False            # 코드 수정 시 자동 reload
    )