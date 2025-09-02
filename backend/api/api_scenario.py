from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from diffusers import DiffusionPipeline
import torch

import models
import scenario
from database import get_db
from config import *

router = APIRouter(prefix="/api", tags=["scenario"])




class setup(BaseModel):
    width: int
    height: int

class TopicRequest(BaseModel):
    user_id: str 
    user_topic_input: str
    title: str  

class ContentsRequest(BaseModel):
    user_id:str
    user_topic_input:str
    topic:str
    description:str
    title:str

class Gen_image_promptRequest(BaseModel):
    user_id:str
    user_topic_input:str
    topic:str
    description:str
    contents_list:list[str]
    title:str

class ImageRequest(BaseModel):
    setup: setup
    user_id: str
    prompt: str
    background: str
    model: str
    image_num: str
    title:str
    block_index: Optional[int] = 0  # block_index 추가

@router.post("/get-scenario-info")
async def generate_scenario(data: TopicRequest, db: Session = Depends(get_db)):
  
    info_str=scenario.get_scenario_info(data.user_topic_input)
    info=scenario.extract_topic_info(info_str)

    return JSONResponse(content={
        "status": "success",
        "topic": info["Topic"],
        "kor_topic": scenario.translate_eng2kor(info["Topic"]),
        "description": info["Description"],
        "kor_description": scenario.translate_eng2kor(info["Description"])
    })

# 1.2 내용 생성
@router.post("/gen_contents")
async def generate_contents(data: ContentsRequest):
    contents = scenario.gen_contents(user_topic_input=data.user_topic_input, topic=data.topic, description=data.description)
    kor_contents = scenario.translate_eng2kor(contents)
    background=scenario.gen_background_prompt(contents)

    return JSONResponse(content={
        "status": "success",
        "background": background,
        "contents": scenario.split_contents(contents),
        "kor_contents": scenario.split_contents(kor_contents)
    })

# 1.3 키프레임 프롬프트 생성
@router.post("gen_image_prompt")
async def generate_image_prompt(data: Gen_image_promptRequest):
    contents=""
    for i in range(len(data.contents_list)):
        contents+=f"#{i+1} {data.contents_list[i]}\n"
    image_prompt=[]
    for i in range(len(data.contents_list)):
        image_prompt.append(scenario.gen_image_prompt(data.user_topic_input, topic=data.topic, description=data.description,content=data.contents_list[i], scenario=contents))
    
    return JSONResponse(content={
        "status": "success",
        "imgage_prompt": image_prompt
    })


@router.post("/generate-first-image")
async def generate_first_image(data: ImageRequest, db: Session = Depends(get_db)):
    image_filename = data.image_num + '.png'
    image_folder= TEMP_DIR / data.user_id / data.title / "keyframe"
    image_folder.mkdir(parents=True,exist_ok=True)
    image_path =  image_folder/image_filename
    block_index = data.block_index

    try:
        if data.model=="dalle-3":
            scenario.gen_dalle_first(data.prompt,data.background,image_path)


        else:
            pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
            pipe.to("cuda")
            prompt = "An astronaut riding a green horse"
            image = pipe(prompt=prompt,
            negative_prompt="(asymmetry, worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch,animation), Beige,open mouth,gray scale,watermark, text, logo, signature" ,
            num_inference_steps=28,
            guidance_scale=5.5,  # 베이스 단독일 때 살짝 높여도 됨
            height=data.setup.height,     
            width=data.setup.width ).images[0]

            image.save(image_path)
        # DB 저장
        # db_item = models.Image(
        #     user_id=data.user_id,
        #     prompt=data.prompt,
        #     model=data.model,
        #     width=data.setup.width,
        #     height=data.setup.height,
        # )
        # db.add(db_item)
        # db.commit()
        # db.refresh(db_item)

        print(f"✅ 이미지 생성 완료: {image_filename}")
        return JSONResponse(content={
            "imageUrl": image_path,
            "status": "success"
        })

    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return JSONResponse(content={
            "imageUrl": f"temp/{data.user_id}/{image_filename}",
            "status": "fail",
            "error": str(e)
        }, status_code=500)



    #연속되는 이미지 생성
@router.post("/generate-series-image")
async def generate_series_image(data: ImageRequest, db: Session = Depends(get_db)):
    image_filename = data.image_num + '.png'
    image_folder= TEMP_DIR / data.user_id / data.title / "keyframe"
    image_folder.mkdir(parents=True,exist_ok=True)
    image_path =  image_folder/image_filename
    previous_img=image_folder / str(int(data.image_num)-1)
    block_index = data.block_index

    try:
    
        scenario.gen_dalle_series(data.prompt,data.background,previous_img,image_path)

        # DB 저장
        # db_item = models.Image(
        #     user_id=data.user_id,
        #     prompt=data.prompt,
        #     model=data.model,
        #     width=data.setup.width,
        #     height=data.setup.height,
        # )
        # db.add(db_item)
        # db.commit()
        # db.refresh(db_item)



        print(f"✅ 이미지 생성 완료: {image_filename}")
        return JSONResponse(content={
            "imageUrl": image_path,
            "status": "success"
        })

    except Exception as e:
        print(f"❌ 이미지 생성 실패: {e}")
        return JSONResponse(content={
            "imageUrl": f"temp/{data.user_id}/{image_filename}",
            "status": "fail",
            "error": str(e)
        }, status_code=500)