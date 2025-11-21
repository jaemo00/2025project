import torch, gc
from diffusers import AutoencoderKLWan, WanVACEPipeline
from diffusers.schedulers.scheduling_unipc_multistep import UniPCMultistepScheduler
from diffusers import DiffusionPipeline
import threading

def show_threads():
    print(f"[DEBUG] load_video_pipe 실행 스레드: {threading.current_thread().name}, id={threading.get_ident()}")

    print("[DEBUG] 현재 실행 중인 스레드 목록:")
    for t in threading.enumerate():
        print(" -", t.name, t.ident)    

def load_pipe():
    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
    )
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    show_threads()
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

    show_threads()

    return pipe

def unload_pipe_fully(pipe) -> None:
    names = [
        "unet", "vae",
        "text_encoder", "text_encoder_2", "image_encoder",
        "safety_checker", "feature_extractor",
        "tokenizer", "tokenizer_2",
        "scheduler"
    ]
    for name in names:
        if hasattr(pipe, name):
            try:
                m = getattr(pipe, name)
                # 원치 않으면 to("cpu") 생략 가능. 하지만 권장: VRAM 즉시 하향
                # try: m.to("cpu")
                # except: pass
                del m
                delattr(pipe, name)
            except Exception:
                pass

    del pipe
    gc.collect()
    torch.cuda.empty_cache()

def mem():
    import torch
    a = torch.cuda.memory_allocated() // (1024**2)   # 실제 사용
    r = torch.cuda.memory_reserved()  // (1024**2)   # 캐시 포함 예약
    print(f"[before] allocated={a} MiB, reserved={r} MiB")