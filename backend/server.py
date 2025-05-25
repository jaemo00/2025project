import torch
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
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
from langchain import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from sqlalchemy.orm import Session
import models
from database import engine, Base, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API KEY 정보로드
load_dotenv()

Base.metadata.create_all(bind=engine)

'''
#영상 모델
pipeline = I2VGenXLPipeline.from_pretrained("ali-vilab/i2vgen-xl", torch_dtype=torch.float16, variant="fp16")
pipeline.enable_model_cpu_offload()
'''

#데이터 파싱
class setup(BaseModel):
    width: int
    height: int

class ImageRequest(BaseModel):
    setup: setup
    userid: str
    prompt: str
    model: str

class VideoRequest(BaseModel):
    userid: str
    imagePrompt: str
    videoPrompt: str
    
class scenarioRequest(BaseModel):
    userid: str
    prompt: str   

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
    user_folder = os.path.join(TEMP_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)
    print(f"{user_id}")

    try:
        while True:
            data = await websocket.receive_text()
            # 필요하면 처리
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")



# frontend 폴더 mount
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
app.mount(
    "/assets",
    StaticFiles(directory=ASSETS_DIR),  
    name="assets"
)
# static 파일들 mount
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")









@app.post("/api/generate-image")
async def generate_image(data: ImageRequest, db: Session = Depends(get_db)):

    """클라이언트에서 JSON 데이터를 받아 응답하는 핸들러"""
    try:
        #이미지 모델
        model_url=os.path.join("C:/Users/AhnLab/Desktop",data.model)
        print(model_url)
        '''
        pipe = StableDiffusionPipeline.from_single_file(
            "C:/Users/AhnLab/Desktop/DreamShaper_8.safetensors",  # DreamShaper 파일 경로
            torch_dtype=torch.float16,
            safety_checker=None,  # 필요 시 꺼줄 수 있음
        )
        pipe = pipe.to("cuda")
        print(torch.cuda.is_available())

        generator = torch.manual_seed(33)

        image = pipe(data.prompt, generator=generator,width=data.setup.width,height=data.setup.height, num_inference_steps=30).images[0]
        '''
        image_filename=data.prompt+'.png'
        print(f"\n{data.setup.width},{data.setup.height},{data.model}")

        user_folder = os.path.join(TEMP_DIR, data.userid)
        
        image_path = os.path.abspath(os.path.join(user_folder, image_filename))
        #image.save(image_path)
        
        db_item = models.Image(
            user_id=data.userid,
            prompt= f"temp/{data.userid}/{image_filename}",
            model=data.model,
            width=data.setup.width,
            height=data.setup.height,
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        print(f"Received text: {image_filename}") 

        if not os.path.exists(image_path):
            image_path = os.path.join(TEMP_DIR, "default.png")  # 기본 이미지 반환
        print(f"path:{image_path}")
        return JSONResponse(content={"imageUrl": f"temp/{data.userid}/{image_filename}","status":"success"})
        

    except Exception as e:
        return JSONResponse(content={"imageUrl": f"temp/{data.userid}/{image_filename}","status":"success"})
    


@app.post("/api/generate-video")
async def generate_video(data: VideoRequest):

    """클라이언트에서 JSON 데이터를 받아 응답하는 핸들러"""
    try:
        user_id = data.userid
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


def init_model():
    MODEL_NAME = 'gpt-3.5-turbo'
    return ChatOpenAI(model=MODEL_NAME, temperature=0.5)

@app.post("/api/generate-scenario")
async def generate_scenario(data: scenarioRequest, db: Session = Depends(get_db)):
    llm = init_model()
    template = '''
    You are a scenario writer.
    You must write a simple 30-second scenario based on the user's input topic.
    Please answer in Korean and format it as a paragraph.

    Paragraph: {paragraph}
    '''
    prompt = PromptTemplate.from_template(template=template)

    summarize_chain = prompt | llm | StrOutputParser()
    result=summarize_chain.invoke(dict(paragraph=data.prompt))
    print(result)

    db_item = models.Scenario(user_id=data.userid, content=result)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return JSONResponse(content={"scenario":result ,"status":"success"})

@app.get("/api/saved/{user_id}")
def get_user_texts(user_id: str, db: Session = Depends(get_db)):
    print("잘 실행됨")
    scenario = db.query(models.Scenario).filter(models.Scenario.user_id == user_id).all()
    image = db.query(models.Image).filter(models.Image.user_id==user_id).all()

    data_scenario = [{"id": item.id, "Scenario": item.content} for item in scenario]
    data_image = [{"id":item.id,"image":item.prompt,"model":item.model,"width":item.width,"height":item.height} for item in image]

    return JSONResponse(content={"user_id": user_id, "Scenario": data_scenario, "image":data_image})


@app.get('/',response_class=HTMLResponse)
async def serve_frontend():
    print("/ 실행")
    with open(os.path.join(DIST_DIR, "index.html"), encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

#fallback함수 : vue에서 처리할 경로의 요청은 index.html 보냄
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def fallback(full_path: str):
    print("폴백함수 실행")
    if full_path.startswith("ws"):
        return HTMLResponse(status_code=404, content="웹소켓은 FastAPI가 처리함")
    return FileResponse(os.path.join(DIST_DIR, "index.html"))


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
