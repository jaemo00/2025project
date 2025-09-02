from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64
from openai import OpenAI
import os,re


load_dotenv()

def trranslate_model():
    MODEL_NAME = 'gpt-3.5-turbo'
    return ChatOpenAI(model=MODEL_NAME, temperature=0.0, api_key = os.getenv("OPENAI_API_KEY"))


def translate_eng2kor(eng):

    llm = trranslate_model()
    template = '''
    You are a professional translator.

    Translate the following English scenario idea into natural and fluent Korean.
    Make sure the translation preserves the meaning, nuance, and tone of the original text.
    If the input contains cultural or contextual elements, adapt them appropriately for a Korean audience.
    Do not explain the translation — only return the translated Korean text.

    English Scenario:
    {scenario}
    '''
    prompt = PromptTemplate.from_template(template=template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"scenario": eng})


def translate_kr2eng(kor):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    llm = trranslate_model()
    template = '''
    You are a professional translator.

    Translate the following Korean scenario idea into natural and fluent English.
    Make sure the translation preserves the meaning, nuance, and tone of the original text.
    If the input contains cultural or contextual elements, adapt them appropriately for an English-speaking audience.
    Do not explain the translation — only return the translated English text.
    **Do not include any titles, headers, or introductory labels such as "English Translation:". Return only the translated content.**

    Korean Scenario:
    {scenario}
    '''
    prompt = PromptTemplate.from_template(template=template)

    summarize_chain = prompt | llm | StrOutputParser()
    return summarize_chain.invoke(dict(scenario=kor))


def get_scenario_info(user_topic):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template = '''
You are a concise planner for YouTube Video.

Write only two short lines in English:
Topic : <rephrase the main topic of the Shorts in 3 words or less, without numbers, time information, or extra details>
Description : <one concise line describing the situation>

Input topic: {topic}
'''

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": user_topic})


# Topic 과 Description 추출
def extract_topic_info(text):    
    topic_match = re.search(r'Topic\s*:\s*(.+)', text)
    desc_match = re.search(r'Description\s*:\s*(.+)', text, re.DOTALL)

    return {
        'Topic': topic_match.group(1).strip() if topic_match else None,
        'Description': desc_match.group(1).strip() if desc_match else None
    }


#콘텐츠 생성
def gen_contents(user_topic_input,topic,description):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template ="""
You are a senior video scriptwriter for videos. 

Using the inputs, write a **highly detailed** video plan split into **2.5-second beats** for a **one-take continuous shot**.

[Inputs] 
- User Topic Input: {user_topic_input} 
- Topic: {topic} 
- Description: {description}

[Important Instruction] 
- The entire output must be written **in English only**, regardless of the input language.
- Each 2.5-second beat must be written as:
  #1: contents 
  #2: contents
  #3: contents
  ...
  #N: contents
- Do not include any headers, explanations, or text before/after the beats.
- If the User Topic Input contains any time-related information (e.g., "30 seconds", "1 minute"), you MUST strictly calculate the total number of beats as:
  total_beats = (total_seconds) ÷ 2.5 + 1
  For example:
    • "15 seconds" → exactly 7 beats
    • "30 seconds" → exactly 13 beats
    • "1 minute" → exactly 25 beats
    • "45 seconds" → exactly 19 beats
- Do NOT generate more or fewer beats than this exact number. The count of beats must be strictly equal to total_beats.
- total_beats must be an odd number.
- If there is NO time-related information in User Topic Input, default to 13 beats (30 seconds).
"""


    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"user_topic_input": user_topic_input, "topic": topic, "description": description})

def split_contents(contents: str):
    """
    Split contents string into a list of segments using '#N:' markers.
    Each segment will NOT include the '#N:' part.
    """
    import re

    # '#숫자:' 패턴 기준으로 split
    parts = re.split(r'#\d+:\s*', contents.strip())

    # 빈 문자열 제거
    segments = [p.strip() for p in parts if p.strip()]

    return segments


#이미지 프롬프트 생성
def gen_image_prompt(user_topic_input, topic, description, content, scenario):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template = """
You are a professional prompt engineer for generative image AI models.

Your task:
- Understand high-level context from **User Topic Input**, **Topic**, **Description**, and **Scenario** (the full script).
- Interpret the **Content**, which is a 2.5-second video beat generated by a large language model.
- Based on all of this, write a **highly detailed English prompt** that can be used as input for an image generation AI model.
- The prompt must strictly describe what should be visually shown in **one single image** corresponding to the **2.5-second beat**.
- Since this video is designed as a **one-take continuous shot**, ensure the image reflects continuity of characters, wardrobe, props, setting, and atmosphere across the Scenario, without implying cuts or scene transitions.
- Use **Scenario** only for continuity (characters, wardrobe, props, setting consistency, era, mood). Do **not** summarize Scenario; focus the image strictly on the **Content** beat.

Strong constraints:
- Focus only on visible elements: characters, actions, expressions, wardrobe, setting, time-of-day/lighting, objects, and atmosphere.
- Do not include: camera directions, lens/FOV, shot types, negative prompts, model/style keywords (e.g., “cinematic, 4k, ultra realistic”).
- Do not include content that could be flagged by OpenAI’s image safety filters: violence, sexual/explicit content, self-harm, political figures, sensitive events, famous people, brand names, or logos.

[Inputs]
- User Topic Input: {user_topic_input}
- Topic: {topic}
- Description: {description}
- Scenario (full script for continuity only): {scenario}
- Content (the specific 2.5-second beat to visualize): {content}

[Output Rules]
- Write only **one single sentence**.
- Do not start with dashes (-), bullet points, or quotation marks (" ").
- The output must begin directly with the description.
- Output must be in plain text with no extra formatting.

[Output]
<one detailed English prompt describing the exact scene for the 2.5-second beat>
"""

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "user_topic_input": user_topic_input,
        "topic": topic,
        "description": description,
        "content": content,
        "scenario": scenario
    })

def gen_background_prompt(contents):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template ="""
You are a professional prompt engineer for generative image AI models.

Your task:
- Read the **contents**
- From them, extract the common setting, background, mood, and atmosphere that should remain consistent across all images in a video.
- Write one single sentence in English that describes this consistent background context.
- The output must emphasize realism and visual continuity (e.g., photo-realistic, natural colors, consistent lighting).
- Do not include quotation marks, dashes, negative prompts, or style keywords like “cinematic, 4k, ultra realistic.”
- Focus only on describing the environment and general atmosphere, not the characters or their actions.

[Inputs]
- contents: {contents}

[Output]
<one detailed English sentence describing the consistent background and atmosphere>
"""


    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({contents})




def gen_dalle_first(prompt,background,save_dir):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # dall-e-3 이미지 생성
    result = client.images.generate(
    model="dall-e-3",
    prompt=(prompt
        + ", " + background
        + ", highly detailed, photo-realistic, natural colors, realistic photography, no cartoon, no illustration"),
    size="1024x1024",
    response_format="b64_json"
    )
    # base64 → bytes 변환
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    # 저장
    with open(save_dir, "wb") as f:
        f.write(image_bytes)

#연속이미지 생성함수
def gen_dalle_series(prompt,background,previous_img,save_dir):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open(previous_img, "rb") as img_fp:
        result = client.images.edit(
            model="gpt-image-1",
            image=img_fp,
            prompt=(  prompt + ", " + background
        + ", highly detailed, photo-realistic, natural colors, realistic photography, no cartoon, no illustration"
    )       ,
            n=1,
            size="1024x1024",
        )

    image_b64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_b64)

    with open(save_dir, "wb") as f:
        f.write(image_bytes)        




def gen_video_prompt(user_topic_input,topic,description, content,background_prompt,current_content,middle_content,next_content,first_prompt,middle_prompt,last_prompt):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template ="""
You are a prompt generation specialist whose goal is to write the high-quality English prompts for video generation by referring to the details of the three images and input, making them more complete and expressive while maintaining the original meaning. The video you need to create is one cut of the entire video. you need to create a prompt, strictly adhering to the formatting of the examples provided.
    Task Requirements:
    1. Descriptions of three images will be given, the first is the first frame of the video, and the second is the middle frame of the video and the third is the last frame of the video. You need to create a prompt so that the three photos connect naturally.
    2. reasonably infer and supplement details without changing the original meaning, making the video more complete and visually appealing
    3. Improve the characteristics of the main subject in the image description (such as appearance, expression, quantity, ethnicity, posture, etc.), rendering style, spatial relationships, and camera angles
    4. Consider the overall content of the video and what the user is trying to create.
    5. The overall output should be in English
    6. The prompt should match the user’s intent and provide a precise and detailed style description. If the user has not specified a style, you need to carefully analyze the style of the provided photo and use that as a reference for writing
    7. You need to emphasize movement information in the input and different camera angles
    8. Your output should convey natural movement attributes, incorporating natural actions related to the described subject category, using simple and direct verbs as much as possible
    9. You should reference the detailed information in the image, such as character actions, clothing, backgrounds, and emphasize the details in the photo
    10. You need to emphasize potential changes that may occur between the two frames, such as "walking into", "appearing", "turning into", "camera left", "camera right", "camera up", "camera down", etc.
    11. Control the prompt to around 80-100 words. Include only the necessary information and do not expand it unnecessarily
    
    Example of the English prompt:
    1. A Japanese fresh film-style photo of a young East Asian girl with double braids sitting by the boat. The girl wears a white square collar puff sleeve dress, decorated with pleats and buttons. 
    She has fair skin, delicate features, and slightly melancholic eyes, staring directly at the camera. Her hair falls naturally, with bangs covering part of her forehead. She rests her hands on the boat, appearing natural and relaxed. The background features a blurred outdoor scene, with hints of blue sky, 
    mountains, and some dry plants. The photo has a vintage film texture. A medium shot of a seated portrait.
    2. An anime illustration in vibrant thick painting style of a white girl with cat ears holding a folder, showing a slightly dissatisfied expression. 
    She has long dark purple hair and red eyes, wearing a dark gray skirt and a light gray top with a white waist tie. The background has a light yellow indoor tone, with faint outlines of some furniture visible. A pink halo hovers above her head, in a smooth Japanese cel-shading style. A close-up shot from a slightly elevated perspective.
    3. CG game concept digital art featuring a huge crocodile with its mouth wide open, with trees and thorns growing on its back. The crocodile's skin is rough and grayish-white, resembling stone or wood texture. Its back is lush with trees, shrubs, and thorny protrusions. With its mouth agape, the crocodile reveals a pink tongue and sharp teeth. 
    The background features a dusk sky with some distant trees, giving the overall scene a dark and cold atmosphere. A close-up from a low angle.
    4. In the style of an American drama promotional poster, Walter White sits in a metal folding chair wearing a yellow protective suit, with the words "Breaking Bad" written in sans-serif English above him, surrounded by piles of dollar bills and blue plastic storage boxes. He wears glasses, 
    staring forward, dressed in a yellow jumpsuit, with his hands resting on his knees, exuding a calm and confident demeanor. The background shows an abandoned, dim factory with light filtering through the windows. There’s a noticeable grainy texture. A medium shot with a straight-on close-up of the character.
    
    Directly output the generated English text.

    Input field description:
- **first image description (`{first_prompt}`)**: This is a description of the starting frame of the scene you are currently creating from the entire video.
- **middle image description (`{middle_prompt}`)**: Visual description of the middle frame of this cut.  
- **last image description (`{last_prompt}`)**: This is a description of the last frame of the scene you are currently creating in the entire video.
- **User Topic Input (`{user_topic_input}`)**: User-provided topic keywords or simple requests. For example, “Video of melting chocolate.”
- **Topic (`{topic}`)**: The main topic of the video. For example, “Expressing the texture of high-quality dark chocolate.”
- **Description (`{description}`)**: A summary and description of the overall mood of the video. For example, “A scene of chocolate slowly melting in a quiet and sensual atmosphere.”
- **Whole Content (`{content}`)**: Full content of the video to be created
- **Background (`{background_prompt}`)**: The overall background and style directive. For example, “Luxurious interior, soft natural light, cinematic style.”

- **Current content ('{current_content}')**: Narrative description of what happens at the start of this scene.
- **Middle content ('{middle_content})**: Narrative description of what happens in the middle of this scene.
- **Next contetnt ('{next_content}')**: Narrative description of what happens at the end of this scene, leading into the next one.


[Input]
-first image description: {first_prompt}
-middle image description: {middle_prompt}
-last image description: {last_prompt}
-User Topic Input: {user_topic_input}
-Topic: {topic}
-Description: {description}
-Whole Content: {content}
-Background: {background_prompt}
-Current content: {current_content}
-middle content: {middle_content}
-Next content: {next_content}

output rules:
- Directly output the generated English text.
- Do NOT include labels like [Video Prompt], PROMPT:, CAMERA:, LIGHTING:, STYLE: in the final output.
- No brackets, tags, or section headers in the output.

"""
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"user_topic_input": user_topic_input, "topic": topic, "description": description, "content":content,"background_prompt":background_prompt,"current_content":current_content,"middle_content":middle_content,"next_content":next_content,"first_prompt":first_prompt,"middle_prompt":middle_prompt,"last_prompt":last_prompt})




