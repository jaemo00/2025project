from diffusers import DiffusionPipeline
from diffusers import StableDiffusionPipeline
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import asyncio
from sqlalchemy import select
import torch

from utils.utils_model import load_pipe
import models
from database import get_db
from utils.scenario import gen_dalle_first,gen_dalle_series
from utils.config import *

router = APIRouter(prefix="/api", tags=["image"])

class setup(BaseModel):
    width: int
    height: int

class ImageRequest(BaseModel):
    setup: setup
    user_id: str
    project_id: int
    prompt: str
    model: str
    image_num: str



@router.post("/generate_first_image")
async def generate_first_image(data: ImageRequest,request:Request, db: Session = Depends(get_db)):
    image_filename = data.image_num + '.png'
    image_folder= TEMP_DIR / data.user_id / str(data.project_id) / "keyframe"
    image_folder.mkdir(parents=True,exist_ok=True)
    image_path =  image_folder/image_filename
    total_steps = 40

    background = models.get_scenario_value(db,data.user_id,data.project_id,"background") or ""

    try:
        if data.model=="dalle-3":
            gen_dalle_first(data.setup.width,data.setup.height,data.prompt,background,image_path)


        else:

            print(f"image_prompt:{data.prompt}")
            async with request.app.state.model_lock:
                if request.app.state.pipe is None:
                    request.app.state.pipe = await asyncio.to_thread(load_pipe)

            ws = request.app.state.active_websockets.get(data.user_id)
            if ws:
                await ws.send_json({"progress": 0})
            else:
                print(f"[WS] no websocket for user_id={data.user_id}, skip progress")
            # 3) 스레드-안전 콜백
            def step_callback(step: int, timestep: int, latents):
                current_step = step + 1
                progress = int(current_step / total_steps * 100)
                ws = request.app.state.active_websockets.get(data.user_id)
                loop = getattr(request.app.state, "EMIT_LOOP", None)
                if ws and loop:
                    loop.call_soon_threadsafe(
                        asyncio.create_task,
                        ws.send_json({"type":"img_progress","progress": progress})
                    )
            
    

        # 4) 무거운 추론은 옆손에서 실행 → 이벤트 루프가 WS를 바로 처리 가능
            def run_pipeline_blocking():
                image = request.app.state.pipe(
                prompt=data.prompt+ ", " + background+ ", highly detailed, photo-realistic, natural colors, realistic photography, no cartoon, no illustration",
                negative_prompt="(asymmetry, worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch,animation), Beige,open mouth,gray scale,watermark, text, logo, signature" ,
                num_inference_steps=40,
                guidance_scale=5.5,  # 베이스 단독일 때 살짝 높여도 됨
                height=data.setup.height,     
                width=data.setup.width ,
                callback=step_callback,
                callback_steps=1,
                generator = torch.Generator(device="cuda").manual_seed(42)
                ).images[0]
                image.save(image_path)
            async with request.app.state.gpu_sem:
                await asyncio.to_thread(run_pipeline_blocking)

        # DB 저장
        existing = db.execute(
            select(models.Image)
            .where(
                models.Image.user_id == data.user_id,
                models.Image.project_id == data.project_id,
            )
            .order_by(models.Image.id.desc())   # 같은 쌍이 여러 행이면 가장 최근 것 선택
            .limit(1)
        ).scalar_one_or_none()

        if existing is None:
            # 2-A) 없으면 새로 생성
            db_item = models.Image(
                user_id=data.user_id,
                project_id=data.project_id,
                image_prompt=[data.prompt],     # 처음 프롬프트로 리스트 생성
                model=data.model,
                width=data.setup.width,
                height=data.setup.height,
            )
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            # db.begin() 컨텍스트가 끝날 때 자동 commit
        else:
            # 2-B) 있으면 수정
            existing.model = data.model
            existing.width = data.setup.width
            existing.height = data.setup.height
            existing.image_prompt[0]=data.prompt
            db.commit()
            db.refresh(existing)
        print("db 업데이트 완료")    

        print(f"✅ 이미지 생성 완료: {image_filename}")
        return JSONResponse(content={
            "imageUrl": str(image_path),
            "status": "success"
        })

    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return JSONResponse(content={
            "imageUrl": f"temp/{data.user_id}/{image_path}",
            "status": "fail",
            "error": str(e)
        }, status_code=500)



    #연속되는 이미지 생성
@router.post("/generate_series_image")
async def generate_series_image(data: ImageRequest,request:Request, db: Session = Depends(get_db)):
    image_filename = data.image_num + '.png'
    image_folder= TEMP_DIR / data.user_id / str(data.project_id) / "keyframe"
    image_folder.mkdir(parents=True,exist_ok=True)
    image_path =  image_folder/image_filename
    previous_img=image_folder / f"{str(int(data.image_num)-1)}.png"

    background = models.get_scenario_value(db,data.user_id,data.project_id,"background") or ""
    print(f"------{background}--------")
    try:
    
        gen_dalle_series(data.setup.width,data.setup.height,data.prompt,background,previous_img,image_path)

        img = db.execute(
            select(models.Image)
            .where(models.Image.user_id == data.user_id, models.Image.project_id == data.project_id)
            .order_by(models.Image.id.desc())        # 여러 행 가능할 때 가장 최근 것 1개
            .limit(1)
        ).scalar_one_or_none()

        if img is None:
            raise RuntimeError("이미지 행을 찾을 수 없습니다. (user_id, project_id) 조합 확인")

        # 리스트 초기화(혹시 None일 수 있으니 방어)
        if img.image_prompt is None:
            img.image_prompt = []

        # 없으면 append, 있으면 교체
        if int(data.image_num) <= len(img.image_prompt):
            img.image_prompt[int(data.image_num)-1] = data.prompt
        else:
            img.image_prompt.append(data.prompt)
        db.commit()
        db.refresh(img)
        print("업데이트 완료:", img.image_prompt)



        print(f"✅ 이미지 생성 완료: {image_filename}")
        return JSONResponse(content={
            "imageUrl": str(image_path),
            "status": "success"
        })

    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return JSONResponse(content={
            "imageUrl": f"temp/{data.user_id}/{image_path}",
            "status": "fail",
            "error": str(e)
        }, status_code=500)