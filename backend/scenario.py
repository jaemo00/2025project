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




def gen_dalle(prompt,background,save_dir):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    # dall-e-3 이미지 생성
    result = client.images.generate(
    model="dall-e-3",
    prompt=(prompt,
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
        








