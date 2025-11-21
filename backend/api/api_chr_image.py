
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import asyncio
from sqlalchemy import select
import torch,gc

from utils.utils_model import load_pipe
import models
from database import get_db
from app_core import app
from utils.scenario import gen_dalle_first
from utils.config import *
import utils.chr_scenario as chr_scenario

router = APIRouter(prefix="/api", tags=["chr_image"])


class setup(BaseModel):
    width: int
    height: int

class Chr_Gen_Image(BaseModel):
    user_id:str
    project_id : int
    setup:setup
    model: str
    character_prompt : str
    image_num:str

class Chr_Image_Request(BaseModel):
    user_id:str
    project_id:int
    setup:setup
    model:str
    prompt:str
    image_num:str




@router.post("/gen_character_image")
async def chr_gen_image(data: Chr_Gen_Image,request:Request, db: Session = Depends(get_db)):
    image_dir=TEMP_DIR / data.user_id / str(data.project_id) /"character"
    image_dir.mkdir(parents=True,exist_ok=True)
    image_path=image_dir/"character.png"

    total_steps=40
    if data.model=="dalle-3":
        gen_dalle_first(data.setup.width,data.setup.height,data.character_prompt,", plain background",str(image_path))
    else :

        print(f"image_prompt:{data.character_prompt}")
        async with request.app.state.model_lock:
            if request.app.state.pipe is None:
                request.app.state.pipe = await asyncio.to_thread(load_pipe)


        await request.app.state.active_websockets[data.user_id].send_json({"progress":0})

        def step_callback(step: int, timestep: int, latents):
            current_step = step + 1
            progress = int(current_step / total_steps * 100)
            request.app.state.EMIT_LOOP.call_soon_threadsafe(
            asyncio.create_task,
            request.app.state.active_websockets[data.user_id].send_json({"progress": progress})
        )

    # 4) 무거운 추론은 옆손에서 실행 → 이벤트 루프가 WS를 바로 처리 가능
        def run_pipeline_blocking():
            image = request.app.state.pipe(
            prompt=data.character_prompt,
            negative_prompt="(asymmetry, worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch,animation), Beige,open mouth,gray scale,watermark, text, logo, signature" ,
            num_inference_steps=total_steps,
            guidance_scale=5.5,  # 베이스 단독일 때 살짝 높여도 됨
            height=data.setup.height,     
            width=data.setup.width ,
            callback=step_callback,
            callback_steps=1,
            generator = torch.Generator(device="cuda").manual_seed(42)
            ).images[0]
            image.save(image_path)

        await asyncio.to_thread(run_pipeline_blocking)

    # DB 저장
    existing = db.execute(
        select(models.Chr_Scenario)
        .where(
            models.Image.user_id == data.user_id,
            models.Image.project_id == data.project_id,
        )
        .order_by(models.Chr_Scenario.id.desc())   # 같은 쌍이 여러 행이면 가장 최근 것 선택
        .limit(1)
    ).scalar_one_or_none()

    if existing is None:
        # 2-A) 없으면 새로 생성
        db_item = models.Chr_Scenario(
            user_id=data.user_id,
            project_id=data.project_id,
            character_prompt=data.character_prompt,     # 처음 프롬프트로 리스트 생성
            model=data.model,
        )
        db.add(db_item)
        # db.begin() 컨텍스트가 끝날 때 자동 commit
    else:
        # 2-B) 있으면 수정
        existing.model = data.model
        existing.character_prompt=data.character_prompt

    db.commit()
    db.refresh(existing)
    print("업데이트 완료:", existing.character_prompt)    


    print(f"캐릭터 생성 완료: {image_path}")
    return JSONResponse(content={
        "imageUrl": str(image_path),
        "status": "success"
    })



@router.post("/chr_generate_first_image")
async def chr_first_image(data:Chr_Image_Request, db: Session = Depends(get_db)):
    save_dir=TEMP_DIR/data.user_id/data.project_id/"keyframe"/ "1.png"
    character_path=TEMP_DIR / data.user_id / str(data.project_id) /"character"/"character.png"
    background=models.get_chr_scenario_value(db,data.user_id,data.project_id,"background")
    name=models.get_chr_scenario_value(db,data.user_id,data.project_id,"character")
    chr_scenario.gen_dalle_chr_first(data.setup.width,data.setup.height,data.prompt,background,name,save_dir,character_path)
    return JSONResponse(content={
        "imageUrl":str(save_dir),
        "status":"success"
    })


@router.post("/chr_generate_series_image")
async def chr_series_image(data:Chr_Image_Request, db: Session = Depends(get_db)):
    save_dir=TEMP_DIR/data.user_id/data.project_id/"keyframe"/ f"{data.image_num}.png"
    prev_dir=TEMP_DIR/data.user_id/data.project_id/"keyframe"/ f"{str(int(data.image_num)-1)}.png"
    char_dir=TEMP_DIR / data.user_id / str(data.project_id) /"character"/"character.png"
    background=models.get_chr_scenario_value(db,data.user_id,data.project_id,"background")
    name=models.get_chr_scenario_value(db,data.user_id,data.project_id,"character")
    prompt_list=models.get_chr_image_value(db,data.user_id,data.project_id,"image_prompt")
    chr_scenario.gen_dalle_chr_series(data.setup.width,data.setup.height,data.prompt,prompt_list[int(data.image_num)-2],background,name,prev_dir,save_dir,char_dir)
    return JSONResponse(content={
        "imageUrl":str(save_dir),
        "status":"success"}
    )





