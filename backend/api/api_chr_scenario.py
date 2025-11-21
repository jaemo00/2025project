from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import torch,gc
from sqlalchemy import select
import PIL.Image as Image
from diffusers.utils import export_to_video, load_image
from utils.utils_model import unload_pipe_fully, load_video_pipe
import asyncio

from utils.scenario import gen_dalle_first
from get_last_frame import get_last_frame
from api.api_video import combine_video
import models
import utils.chr_scenario as chr_scenario
from database import get_db
from utils.config import *


router = APIRouter(prefix="/api", tags=["chr_scenario"])



class TopicRequest(BaseModel):
    user_id: str 
    project_id:int
    user_topic_input: str
    time : int
    

class Chr_ContentsRequest(BaseModel):
    user_id:str
    project_id:int
    topic:str
    description:str
    character:str
    character_description:str

class Gen_character_prompt(BaseModel):
    user_id:str
    project_id: int
    character_description:str

class Gen_image_promptRequest(BaseModel):
    user_id:str
    project_id:int
    contents_list:list[str]

class AutoRequest(BaseModel):
    user_id:str
    project_id:int
    user_topic_input:str
    time:int
    



# 1.1 토픽생성
@router.post("/chr_get_scenario_info")
async def generate_scenario(data: TopicRequest, db: Session = Depends(get_db)):
    print(f"받은데이터{data.project_id}")
    info_str=chr_scenario.get_scenario_info(data.user_topic_input)
    info=chr_scenario.extract_topic_info(info_str)
    #DB 저장
    existing = db.execute(
            select(models.Chr_Scenario)
            .where(
                models.Chr_Scenario.user_id == data.user_id,
                models.Chr_Scenario.project_id == data.project_id,
            )
            .order_by(models.Chr_Scenario.id.desc())   # 같은 쌍이 여러 행이면 가장 최근 것 선택
            .limit(1)
        ).scalar_one_or_none()
    if existing is None:
        db_item = models.Chr_Scenario(
            user_id=data.user_id,
            project_id=data.project_id,
            user_topic_input=data.user_topic_input,
            time=data.time,
            topic = info["Topic"],
            description = info["Description"],
            character = info["Main Character"],
            character_description = info["Main Character Description"]
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    else:
        # 2-B) 있으면 수정
        existing.user_topic_input = data.user_topic_input
        existing.time=data.time
        existing.topic = info["Topic"]
        existing.description = info["Description"]
        existing.character = info["Main Character"]
        existing.character = info["Main Character Description"]
    db.commit()

    return JSONResponse(content={
        "status": "success",
        "topic": info["Topic"],
        "kor_topic": chr_scenario.translate_eng2kor(info["Topic"]),
        "description": info["Description"],
        "kor_description": chr_scenario.translate_eng2kor(info["Description"]),
        "main_character" : chr_scenario.translate_eng2kor(info["Main Character"]),
        "main_character_description": chr_scenario.translate_eng2kor(info["Main Character Description"])
    })

# 1.2 내용 생성
@router.post("/chr_gen_contents")
async def generate_contents(data: Chr_ContentsRequest,db: Session = Depends(get_db)):
    user_topic_input=models.get_chr_scenario_value(db,data.user_id,data.project_id,"user_topic_input")
    time=models.get_chr_scenario_value(db,data.user_id,data.project_id,"time")
    print(user_topic_input)
    topic=chr_scenario.translate_kr2eng(data.topic); description=chr_scenario.translate_kr2eng(data.description)
    character=chr_scenario.translate_kr2eng(data.character)
    character_description=chr_scenario.translate_kr2eng(data.character_description)
    contents = chr_scenario.gen_contents(user_topic_input,topic, description, character,character_description,int(time/2.5+1))
    kor_contents = chr_scenario.translate_eng2kor(contents)
    background= chr_scenario.gen_background_prompt(contents)
    db.query(models.Chr_Scenario).filter(models.Chr_Scenario.user_id == data.user_id,models.Chr_Scenario.project_id == data.project_id
    ).update({"contents":contents,"background":background,"topic":topic,"description":description,"character":character,"character_description":character_description}, synchronize_session=False)
    db.commit()

    return JSONResponse(content={
        "status": "success",
        "contents": chr_scenario.split_contents(contents),
        "kor_contents": chr_scenario.split_contents(kor_contents)
    })


@router.post("/character_image_prompt")
async def character_image_prompt(data: Gen_character_prompt,db: Session = Depends(get_db)):
    user_topic_input=models.get_chr_scenario_value(db,data.user_id,data.project_id,"user_topic_input")
    character_prompt=chr_scenario.character_image_prompt(user_topic_input, data.character_description)

    return JSONResponse(content={
        "status":"success",
        "character_prompt":character_prompt
    })


# 1.3 키프레임 프롬프트 생성
@router.post("/chr_gen_image_prompt")
async def generate_image_prompt(data: Gen_image_promptRequest,db: Session = Depends(get_db)):
    user_topic_input=models.get_chr_scenario_value(db,data.user_id,data.project_id,"user_topic_input")
    topic=models.get_chr_scenario_value(db,data.user_id,data.project_id,"topic")
    description=models.get_chr_scenario_value(db,data.user_id,data.project_id,"description")

    contents=""
    for i in range(len(data.contents_list)):
        contents+=f"#{i+1} {chr_scenario.translate_kr2eng(data.contents_list[i])}\n"
    print(contents)

    image_prompt=[]
    for i in range(len(data.contents_list)):
        image_prompt.append(chr_scenario.gen_image_prompt(user_topic_input, topic=topic, description=description,content=chr_scenario.translate_kr2eng(data.contents_list[i]), scenario=contents))

    kor_image_prompt=[]
    for i in range(len(image_prompt)):
        kor_image_prompt.append(chr_scenario.translate_eng2kor(image_prompt[i]))

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
            image_prompt=image_prompt,     # 처음 프롬프트로 리스트 생성
        )
        db.add(db_item)
        # db.begin() 컨텍스트가 끝날 때 자동 commit
    else:
        # 2-B) 있으면 수정
        existing.image_prompt=image_prompt
    db.commit()
        
    return JSONResponse(content={
        "status": "success",
        "image_prompt": image_prompt,
        "kor_image_prompt": kor_image_prompt
    })


@router.post("/chr_auto")
async def ocastrater(request: Request,data:AutoRequest,db: Session = Depends(get_db)):
    active_websockets=request.app.state.active_websockets
    # 1단계 
    info=chr_scenario.extract_topic_info(chr_scenario.get_scenario_info(data.user_topic_input))
    print("1단계 완료 ")
    await active_websockets[data.user_id].send_json({
        "status": "info success",
        "topic" : info["Topic"],
        "kor_topic": chr_scenario.translate_eng2kor(info["Topic"]),
        "description": info["Description"],
        "kor_description": chr_scenario.translate_eng2kor(info["Description"]),
        "character": chr_scenario.translate_eng2kor(info["Main Character"]),
        "character_description": chr_scenario.translate_eng2kor(info["Main Character Description"])
    }
    )

    # 2단계 
    contents=chr_scenario.gen_contents(data.user_topic_input,info["Topic"],info["Description"],info["Main Character"],info["Main Character Description"],int(data.time/2.5+1))
    contents_list=chr_scenario.split_contents(contents)
    kor_contents = chr_scenario.translate_eng2kor(contents)
    background=chr_scenario.gen_background_prompt(contents)
    print(f"2단계 완료 - contetnts: {contents_list}")
    await active_websockets[data.user_id].send_json({
        "status": "content success",
        "contents": chr_scenario.split_contents(contents),
        "kor_contents": chr_scenario.split_contents(kor_contents)
    })

    #3단계 캐릭터 프롬프트 생성
    character_prompt=chr_scenario.character_image_prompt(data.user_topic_input, info["Main Character Description"])
    await active_websockets[data.user_id].send_json({
        "status" : "character prompt success",
        "character_prompt" :character_prompt
    })

    # 4단계 캐릭터 생성
    character_dir=TEMP_DIR / data.user_id / str(data.project_id) /"character"
    character_dir.mkdir(parents=True,exist_ok=True)
    character_path=character_dir / "character.png"
    # gen_dalle_first(1024,1024,character_prompt,", plain background",str(character_path))
    await active_websockets[data.user_id].send_json({
        "status" : "character generate success",
        "character_path" :str(character_path)
    })


    # 5단계 키프레임 프롬프트 생성
    image_prompt=[]
    for i in range(len(contents_list)):
        image_prompt.append(chr_scenario.gen_image_prompt(data.user_topic_input, topic=info["Topic"], description=info["Description"],content=contents_list[i], scenario=contents))
    
    kor_image_prompt=[]
    for i in range(len(image_prompt)):
        kor_image_prompt.append(chr_scenario.translate_eng2kor(image_prompt[i]))

    await active_websockets[data.user_id].send_json({
        "status": "img prompt success",
        "image_prompt": image_prompt,
        "kor_image_prompt": kor_image_prompt
    })

    # 6단계 이미지 생성
    image_dir=TEMP_DIR/data.user_id/str(data.project_id)/"keyframe"
    image_dir.mkdir(parents=True,exist_ok=True)
    chr_scenario.gen_dalle_chr_first(1024,1024,image_prompt[0],background,info["Main Character"],str(image_dir/"1.png"),str(character_path))
    await active_websockets[data.user_id].send_json({   
            "staus": "first img gen success",
            "imageUrl": str(image_dir/"1.png")})
    for idx in range(1, len(image_prompt)):
        chr_scenario.gen_dalle_chr_series(1024,1024,image_prompt[idx],image_prompt[idx-1],background,info["Main Character"],f"{image_dir}/{str(idx)}.png",f"{image_dir}/{str(idx+1)}.png",str(character_path))
        await active_websockets[data.user_id].send_json({
            "staus": f"{str(idx+1)} img gen success",
            "imageUrl": f"{image_dir}/{str(idx+1)}.png"
        })


    # 7단계 동영상 프롬프트 생성
    video_prompt = []
    for i in range(0,len(contents_list)-2,2):
        video_prompt.append(chr_scenario.gen_video_prompt(data.user_topic_input, topic=info["Topic"], description=info["Description"], content=contents,
        background_prompt=background,current_content=contents_list[i],middle_content=contents_list[i+1],next_content=contents_list[i+2], first_prompt=image_prompt[i],middle_prompt=image_prompt[i+1],last_prompt=image_prompt[i+2]))
    kor_video_prompt=[]
    for i in range(len(video_prompt)):
        kor_video_prompt.append(chr_scenario.translate_eng2kor(video_prompt[i])) 
    await active_websockets[data.user_id].send_json({
        "status": "video prompt success",
        "video_prompt": video_prompt,
        "kor_video_prompt": kor_video_prompt
    })

    #8단계 동영상 생성
    async with request.app.state.model_lock:
        if request.app.state.pipe is not None:
            p = request.app.state.pipe
            request.app.state.pipe = None
            unload_pipe_fully(p)

    async with request.app.state.model_lock:
        if request.app.state.video_pipe is None:
            request.app.state.video_pipe = await asyncio.to_thread(load_video_pipe)
   
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
    
    extract_folder= image_dir / "extract"
    video_folder= TEMP_DIR / data.user_id / str(data.project_id) / "video"
    extract_folder.mkdir(parents=True,exist_ok=True)
    video_folder.mkdir(parents=True,exist_ok=True)
    
    total_steps=50

    def make_step_callback(i: int):
        def step_callback(self, step: int, timestep: int, callback_kwargs: dict):
            total = len(self.scheduler.timesteps) if hasattr(self, "scheduler") else total_steps
            current_step = step + 1
            progress = int(current_step / total * 100)
            request.app.state.EMIT_LOOP.call_soon_threadsafe(
                asyncio.create_task,
                request.app.state.active_websockets[data.user_id].send_json({
                    "progress": progress,
                    "video_index": i   
                })
            )
            return callback_kwargs
        return step_callback

    def run_video_blocking(i:int):
        output_path=video_folder / f"{str(i+1)}.mp4"

        negative_prompt = "blurred details, Bright tones, worst quality, low quality, incomplete, ugly"
        if i==0:
            first_frame = load_image(str(image_dir / f"{str(i+1)}.png"))
            middle_frame = load_image(str(image_dir / f"{str(i+2)}.png"))
            last_frame = load_image(str(image_dir / f"{str(i+3)}.png"))
        else:
            first_frame = load_image(str(extract_folder / f"{str(i+1)}_start.png"))
            middle_frame = load_image(str(image_dir / f"{str(i+2)}.png"))
            last_frame = load_image(str(image_dir / f"{str(i+3)}.png"))

        video, mask = prepare_video_and_mask(first_img=first_frame,middle_img=middle_frame, last_img=last_frame, height=720, width=720, num_frames=81)

        output = request.app.state.video_pipe(
            video=video,
            mask=mask,
            prompt=video_prompt[i],
            negative_prompt=negative_prompt,
            height=720,
            width=720,
            num_frames=81,
            num_inference_steps=total_steps,
            guidance_scale=5.0,
            callback_on_step_end=make_step_callback(i),            # ← 콜백 등록
            callback_on_step_end_tensor_inputs=["latents"],
            generator=torch.Generator().manual_seed(42),
        ).frames[0]

        export_to_video(output, str(output_path), fps=16)

        get_last_frame(video_path=str(output_path),save_path=str(extract_folder),i=i+2)

        gc.collect(); torch.cuda.empty_cache()
        request.app.state.EMIT_LOOP.call_soon_threadsafe(
        asyncio.create_task,
        request.app.state.active_websockets[data.user_id].send_json({ 
            "status": f"{str(i+1)} video gen success",
            "video_dir": str(output_path)})
        )
 

    for i in range(len(video_prompt)):
        await asyncio.to_thread(run_video_blocking,i)



    
    #7단계 동영상 병합
    combine_video(video_folder)
    return JSONResponse(content={
        "status": "ALL success",
        "final_video": str(video_folder/"final_video.mp4")
    })







