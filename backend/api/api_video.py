import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128"
# tokenizers 경고 무시
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from fastapi import APIRouter, Depends,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from diffusers.utils import export_to_video, load_image
import PIL.Image as Image
import torch, gc
from sqlalchemy import select
import asyncio


import cv2
from pathlib import Path

from utils.utils_model import load_video_pipe, unload_pipe_fully, show_threads 
import models
from get_last_frame import get_last_frame
from database import get_db
from utils.config import *
import utils.scenario as scenario

router = APIRouter(prefix="/api", tags=["video"])

class VideoPromptRequest(BaseModel):
    user_id:str
    project_id:int

class VideoRequest(BaseModel):
    user_id: str
    project_id: int
    width : int
    height : int
    prompt: str
    cut_num : str
    num_frame : int
    fps:int

class CombineRequest(BaseModel):
    user_id:str
    project_id :int




@router.post("/gen_video_prompt")
async def gen_video_prompt(data:VideoPromptRequest,db: Session = Depends(get_db)):
    stmt = select(models.Scenario).where(models.Scenario.user_id==data.user_id, models.Scenario.project_id==data.project_id).limit(1)
    row = db.execute(stmt).scalar_one_or_none()

    img = db.execute(select(models.Image).where(models.Image.user_id == data.user_id, models.Image.project_id == data.project_id)
    .order_by(models.Image.id.desc()).limit(1)
    ).scalar_one_or_none()

    print(row.contents)
    contents_list=scenario.split_contents(row.contents)

    video_prompt = []
    for i in range(0,len(contents_list)-2,2):
        video_prompt.append(scenario.gen_video_prompt(row.user_topic_input, topic=row.topic, description=row.description, content=row.contents,
        background_prompt=row.background,current_content=contents_list[i],middle_content=contents_list[i+1],next_content=contents_list[i+2], first_prompt=img.image_prompt[i],middle_prompt=img.image_prompt[i+1],last_prompt=img.image_prompt[i+2]))
    kor_video_prompt=[]
    for i in range(len(video_prompt)):
        kor_video_prompt.append(scenario.translate_eng2kor(video_prompt[i]))   

    #db에 저장
    existing = db.execute(
    select(models.Image)
    .where( models.Image.user_id == data.user_id,
        models.Image.project_id == data.project_id,).order_by(models.Image.id.desc()).limit(1)
    ).scalar_one_or_none()  

    existing.video_prompt=video_prompt
    db.commit()
    db.refresh(existing)

    return JSONResponse(content={
        "status": "success",
        "video_prompt": video_prompt,
        "kor_video_prompt": kor_video_prompt
    })


@router.post("/chr_gen_video_prompt")
async def gen_video_prompt(data:VideoPromptRequest,db: Session = Depends(get_db)):
    stmt = select(models.Chr_Scenario).where(models.Chr_Scenario.user_id==data.user_id, models.Chr_Scenario.project_id==data.project_id).limit(1)
    row = db.execute(stmt).scalar_one_or_none()

    img = db.execute(select(models.Image).where(models.Image.user_id == data.user_id, models.Image.project_id == data.project_id)
    .order_by(models.Image.id.desc()).limit(1)
    ).scalar_one_or_none()

    print(row.contents)
    contents_list=scenario.split_contents(row.contents)

    video_prompt = []
    for i in range(0,len(contents_list)-2,2):
        video_prompt.append(scenario.gen_video_prompt(row.user_topic_input, topic=row.topic, description=row.description, content=row.contents,
        background_prompt=row.background,current_content=contents_list[i],middle_content=contents_list[i+1],next_content=contents_list[i+2], first_prompt=img.image_prompt[i],middle_prompt=img.image_prompt[i+1],last_prompt=img.image_prompt[i+2]))
    kor_video_prompt=[]
    for i in range(len(video_prompt)):
        kor_video_prompt.append(scenario.translate_eng2kor(video_prompt[i]))   

    #db에 저장
    existing = db.execute(
    select(models.Image)
    .where( models.Image.user_id == data.user_id,
        models.Image.project_id == data.project_id,).order_by(models.Image.id.desc()).limit(1)
    ).scalar_one_or_none()  

    existing.video_prompt=video_prompt
    db.commit()
    db.refresh(existing)

    return JSONResponse(content={
        "status": "success",
        "video_prompt": video_prompt,
        "kor_video_prompt": kor_video_prompt
    })

@router.post("/gen_video")
async def gen_video(data:VideoRequest,request:Request,db: Session = Depends(get_db)):
    async with request.app.state.model_lock:
        if request.app.state.pipe is not None:
            p = request.app.state.pipe
            request.app.state.pipe = None
            unload_pipe_fully(p)

    async with request.app.state.model_lock:
        if request.app.state.video_pipe is None:
            request.app.state.video_pipe =  await asyncio.to_thread(load_video_pipe)

    def prepare_video_and_mask(first_img: Image.Image, middle_img:Image.Image, last_img: Image.Image,
                            height: int, width: int, num_frames: int):
        assert num_frames >= 2, "num_frames must be >= 2"
        first_img = first_img.resize((width, height))
        middle_img = middle_img.resize((width, height))
        last_img  = last_img.resize((width, height))
        frames = [first_img]
        frames += [Image.new("RGB", (width, height), (128,128,128)) for _ in range(num_frames - 2)]
        frames.append(last_img)
        frames[num_frames//2]=middle_img
        mask_black = Image.new("L", (width, height), 0)
        mask_white = Image.new("L", (width, height), 255)
        mask = [mask_black] + [ mask_white for _ in range(num_frames - 2)] + [mask_black]
        mask[num_frames//2] = mask_black
        return frames, mask

    image_folder= TEMP_DIR / data.user_id / str(data.project_id) / "keyframe"
    extract_folder= image_folder / "extract"
    video_folder= TEMP_DIR / data.user_id / str(data.project_id) / "video"
    extract_folder.mkdir(parents=True,exist_ok=True)
    video_folder.mkdir(parents=True,exist_ok=True)
    output_path=video_folder / f"{data.cut_num}.mp4"

    negative_prompt = "blurred details, Bright tones, worst quality, low quality, incomplete, ugly"
    if data.cut_num=="1":
        first_frame = load_image(str(image_folder / f"{data.cut_num}.png"))
        middle_frame = load_image(str(image_folder / f"{str(int(data.cut_num)+1)}.png"))
        last_frame = load_image(str(image_folder / f"{str(int(data.cut_num)+2)}.png"))
    else:
        first_frame = load_image(str(extract_folder / f"{str(int(data.cut_num)*2-1)}_start.png"))
        middle_frame = load_image(str(image_folder / f"{str(int(data.cut_num)*2)}.png"))
        last_frame = load_image(str(image_folder / f"{str(int(data.cut_num)*2+1)}.png"))


    video, mask = prepare_video_and_mask(first_img=first_frame,middle_img=middle_frame, last_img=last_frame, height=data.height, width=data.width, num_frames=data.num_frame)

    
    await request.app.state.active_websockets[data.user_id].send_json({"progress":0})

    total_steps=50
    def step_callback(self,step: int, timestep: int, callback_kwargs: dict):
        total = len(self.scheduler.timesteps) if hasattr(self, "scheduler") else total_steps
        current_step = step + 1
        progress = int(current_step / total * 100)
        request.app.state.EMIT_LOOP.call_soon_threadsafe(
        asyncio.create_task,
        request.app.state.active_websockets[data.user_id].send_json({"progress": progress})
        )
        return callback_kwargs
    
    def run_video_blocking():
        show_threads()
        output = request.app.state.video_pipe(
            video=video,
            mask=mask,
            prompt=data.prompt,
            negative_prompt=negative_prompt,
            height=data.height,
            width=data.width,
            num_frames=data.num_frame,
            num_inference_steps=total_steps,
            guidance_scale=5.0,
            callback_on_step_end=step_callback,            # ← 콜백 등록
            callback_on_step_end_tensor_inputs=["latents"],
            generator=torch.Generator().manual_seed(42),
        ).frames[0]

        export_to_video(output, str(output_path), fps=data.fps)

        get_last_frame(video_path=str(output_path),save_path=str(extract_folder),i=int(data.cut_num)+1)
    await asyncio.to_thread(run_video_blocking)

    return JSONResponse(content={
        "status": "success",
        "video_dir": str(output_path)
    })




#영상 결합
def combine_video(video_folder:Path):

    video_files = sorted(video_folder.glob("*.mp4"))

    if not video_files:
        raise Exception("폴더에 mp4 파일이 없습니다.")
    print("합칠 영상 목록:")
    for i, f in enumerate(video_files,start=1):
        print(f"{i}:{f}")

    # 첫 번째 영상으로 해상도, FPS 가져오기
    cap = cv2.VideoCapture(str(video_files[0]))
    if not cap.isOpened():
        raise Exception(f"Can't open {video_files[0]}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # 출력 비디오 경로 (Path 객체 사용)
    out_path = video_folder / "final_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(out_path), fourcc, fps, (width, height))

    # 모든 영상을 순차적으로 합치기
    for file in video_files:
        cap = cv2.VideoCapture(str(file))
        if not cap.isOpened():
            print(f"⚠️ {file} 열기 실패, 건너뜁니다.")
            continue

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # 해상도가 다르면 강제로 맞추기
            if frame.shape[1] != width or frame.shape[0] != height:
                frame = cv2.resize(frame, (width, height))
            out.write(frame)

        cap.release()

    out.release()
    print(f"✅ 영상 합치기 완료: {out_path}")


@router.post("/combine")
def combine_func(data:CombineRequest):
    video_dir=TEMP_DIR/data.user_id/str(data.project_id)/"video"
    combine_video(video_dir)
    return JSONResponse(content={
        "status": "success",
        "final_video": str(video_dir/"final_video.mp4")
    })
