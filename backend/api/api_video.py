from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from diffusers import AutoencoderKLWan, WanVACEPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
from diffusers.utils import export_to_video, load_image
from get_last_frame import get_last_frame
import PIL.Image as Image
import torch, gc
import models

from database import get_db
from config import *
import scenario

router = APIRouter(prefix="/api", tags=["video"])

class VideoPromptRequest(BaseModel):
    user_id:str
    user_topic_input:str 
    topic:str
    description:str
    background:str
    contents:str
    contents_list:str
    image_prompt:str
    title: str

class VideoRequest(BaseModel):
    user_id: str
    width : int
    height : int
    prompt: str
    cut_num : str
    num_frame : int
    start:str
    middle:str
    end:str
    fps:int
    image_num: str
    title: str
    block_index: Optional[int] = 0  # block_index 추가

model_id = "Wan-AI/Wan2.1-VACE-1.3B-diffusers"
vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
# bf16이 안 되면 float16/float32로 변경 필요할 수 있음
pipe = WanVACEPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
flow_shift = 3.0  # 480p면 3.0, 720p면 5.0 권장
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=flow_shift)

pipe.to("cuda")
pipe.vae.enable_tiling()
pipe.vae.enable_slicing()


@router.post("gen_video_prompt")
async def gen_video_prompt(data:VideoPromptRequest):
    video_prompt = []
    for i in range(0,len(data.contents_list)-2,2):
        video_prompt.append(scenario.gen_video_prompt(data.user_topic_input, topic=data.topic, description=data.description, content=data.contents,
        background_prompt=data.background,current_content=data.contents_list[i],middle_content=data.contents_list[i+1],next_content=data.contents_list[i+2], first_prompt=data.image_prompt[i],middle_prompt=data.image_prompt[i+1],last_prompt=data.image_prompt[i+2]))
    kor_video_prompt=[]
    for i in range(len(video_prompt)):
        kor_video_prompt.append(scenario.translate_eng2kor(video_prompt[i]))      
    
    return JSONResponse(content={
        "status": "success",
        "video_prompt": video_prompt,
        "kor_video_prompt": kor_video_prompt
    })



@router.post("/gen_video")
async def gen_video(data:VideoRequest):
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

    image_folder= TEMP_DIR / data.user_id / data.title / "keyframe"
    extract_folder= image_folder / "extract"
    video_folder= TEMP_DIR / data.user_id / data.title / "video"
    extract_folder.mkdir(parents=True,exist_ok=True)
    video_folder.mkdir(parents=True,exist_ok=True)
    output_path=video_folder / f"{data.cut_num}.mp4"

    negative_prompt = "blurred details, Bright tones, worst quality, low quality, incomplete, ugly"
    if data.cut_num=="1":
        first_frame = load_image(str(image_folder / f"{data.start}.png"))
        middle_frame = load_image(str(image_folder / f"{data.middle}.png"))
        last_frame = load_image(str(image_folder / f"{data.end}.png"))
    else:
        first_frame = load_image(str(extract_folder / f"{data.start}_start.png"))
        middle_frame = load_image(str(image_folder / f"{data.middle}.png"))
        last_frame = load_image(str(image_folder / f"{data.end}.png"))


    video, mask = prepare_video_and_mask(first_img=first_frame,middle_img=middle_frame, last_img=last_frame, height=data.height, width=data.width, num_frames=data.num_frame)

    output = pipe(
        video=video,
        mask=mask,
        prompt=data.prompt,
        negative_prompt=negative_prompt,
        height=data.height,
        width=data.width,
        num_frames=data.num_frame,
        num_inference_steps=50,
        guidance_scale=5.0,
        generator=torch.Generator().manual_seed(42),
    ).frames[0]

    export_to_video(output, str(output_path), fps=data.fps)

    get_last_frame(video_path=str(output_path),save_path=str(extract_folder),i=int(data.cut_num)+1)

    gc.collect(); torch.cuda.empty_cache()
