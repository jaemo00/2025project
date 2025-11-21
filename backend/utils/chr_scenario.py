from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64
from openai import OpenAI
import os,re
from pathlib import Path



def trranslate_model():
    from langchain_openai import ChatOpenAI
    MODEL_NAME = 'gpt-3.5-turbo'
    return ChatOpenAI(model=MODEL_NAME, temperature=0.0, api_key=os.getenv("OPENAI_API_KEY"))


from langchain_openai import ChatOpenAI

def translate_eng2kor(eng):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser

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
You are a creative assistant helping generate story setup information.

Based on the following topic, write only the following four lines in English:

Topic : <rephrase the main topic of the Shorts in 3 words or less, without numbers, time information, or extra details>
Description : <one concise line describing the situation>
Main Character: <Name>
Main Character Description: <a detailed description of the main character’s appearance>

Topic: {topic}
    '''


    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"topic": user_topic})


import re

def extract_topic_info(text):
    # Topic, Description, Main Character, Main Character Description 추출
    topic_match = re.search(r'Topic\s*:\s*(.+)', text)
    desc_match = re.search(r'Description\s*:\s*(.+)', text)
    main_char_match = re.search(r'Main Character\s*:\s*(.+)', text)
    main_char_desc_match = re.search(r'Main Character Description\s*:\s*(.+)', text, re.DOTALL)

    return {
        'Topic': topic_match.group(1).strip() if topic_match else None,
        'Description': desc_match.group(1).strip() if desc_match else None,
        'Main Character': main_char_match.group(1).strip() if main_char_match else None,
        'Main Character Description': main_char_desc_match.group(1).strip() if main_char_desc_match else None,
    }


def gen_contents(user_topic_input, topic, description, main_character, main_character_description,total_beats):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI

    llm = trranslate_model()

    template = """
You are a senior video scriptwriter for videos.

Using the inputs, write a **highly detailed** video plan split into **2.5-second beats** for a **one-take continuous shot**.

[Inputs]
- User Topic Input: {user_topic_input}
- Topic: {topic}
- Description: {description}
- Main Character Name: {main_character}
- Main Character Description: {main_character_description}
- total_beats : {total_beats}

[Important Instruction]
- The entire output must be written **in English only**, regardless of the input language.
- Output ONLY the beats, one per line, with the exact format:
  #1: <contents>
  #2: <contents>
  ...
  #{total_beats}: <contents>
- Do not include any headers, explanations, or text before/after the beats.
- Number lines as #1, #2, …, #{total_beats}
- Do NOT generate more or fewer beats than this exact number. The count of beats must be strictly equal to total_beats.
"""

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "user_topic_input": user_topic_input,
        "topic": topic,
        "description": description,
        "main_character": main_character,
        "main_character_description": main_character_description,
        "total_beats":total_beats
    })




def split_contents(contents: str):
    """
    Extract only the text segments that follow '#N:' markers.
    """
    segments = re.findall(r'#\d+:\s*(.*?)(?=(#\d+:|$))', contents, flags=re.S)
    return [s[0].strip() for s in segments if s[0].strip()]


def character_image_prompt(user_topic_input, main_character_description):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI

    llm = trranslate_model()

    template = """
You are a professional prompt engineer for generative AI image models.

Analyze the story context and generate ONE single, detailed text prompt that describes the MAIN CHARACTER.  
If the character is a human, describe ONLY the FACE.  
If the character is an animal, describe the FULL BODY clearly so that the entire form is visible, not just the face.  
Do not include background, setting, clothing (for humans), or props.  
Focus strictly on the required traits.

[Story Context]
- User Topic Input: {user_topic_input}
- Main Character Description: {main_character_description}

# Instructions
- The entire output must be **in English only**.
- Output **one single sentence**, plain text, no quotes or bullet points.
- For humans, focus only on:
  * Age range
  * Gender
  * Face shape
  * Eyes (shape, size, color, expression)
  * Nose (size, shape)
  * Mouth & lips (shape, fullness, expression)
  * Skin tone, complexion, distinguishing marks (scars, moles, freckles)
  * Hair (style, length, color, texture) as it frames the face
  * Typical facial expression (skepticism, fear, determination, etc.)
- For animals, focus on:
  * Species and approximate age
  * Overall body size and proportions (make sure the whole body is clearly shown)
  * Fur/feather/scale color, texture, and patterns
  * Distinctive features (ears, tail, paws, wings, etc.)
  * Typical expression or behavior that defines personality
- Do NOT include: background, lighting, props, environment, or cinematic effects.
- Ensure the description is self-contained to visualize the character exactly as intended.
"""

    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "user_topic_input": user_topic_input,
        "main_character_description": main_character_description
    })


def gen_image_prompt(user_topic_input, topic, description, content, scenario):
    from langchain import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    llm = trranslate_model()

    template = """
You are a professional prompt engineer for generative image AI models.

Your task:
- Understand the broader context from **User Topic Input**, **Topic**, **Description**, and **Scenario** (the full script).
- Interpret the **Content**, which is a 2.5-second video beat generated by a large language model.
- Based on all of this, write a **highly detailed English prompt** that can be used as input for an image generation AI model.
- The prompt must strictly describe what should be visually shown in **one single image** corresponding to the **2.5-second beat**.
- Since this video is designed as a **one-take continuous shot**, ensure that the image reflects continuity of characters, setting, atmosphere, and props across the entire Scenario without suggesting cuts or scene transitions.
- Use **Scenario** only for continuity (consistent characters, wardrobe, props, setting, era, and mood); do **not** summarize or restate the Scenario. Focus the image strictly on the **Content** beat.

Strict constraints:
- Focus only on visible elements: characters, actions, expressions, wardrobe, setting, time-of-day/lighting, objects, and atmosphere.
- Do not include camera directions, lens/FOV, shot types, negative prompts, or style keywords (e.g., “cinematic, 4k, ultra realistic”).
- Do not include any content that could be flagged by OpenAI’s image safety filters, such as violence, sexual/explicit content, self-harm, political figures, sensitive events, famous people, brand names, or logos.
- Do NOT include:
   - Any sexual, explicit, or suggestive description (e.g., wet clothes clinging to the body, exposed skin, physical body emphasis).
   - References to violence, blood, weapons, self-harm, abuse, or unsafe situations.
   - Mentions of political figures, celebrities, brands, logos, copyrighted characters, or sensitive real-world events.
   - Overly detailed descriptions of anatomy (e.g., breasts, thighs, skin texture). 
- Use **neutral and artistic descriptions** instead of sensitive words:
   - Instead of “wet clothes sticking to the skin” → say “her clothes appear darker and heavier from the rain.”
   - Instead of “porcelain complexion” → say “her face appears illuminated softly by the light.”
   - Instead of “clinging hair on her skin” → say “her hair looks damp and slightly messy from the rain.”   


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


def gen_dalle_chr_first(width,height,prompt,background,name,save_dir,char_dir):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        input_prompt = (
            prompt + ", " + background + ", highly detailed, photo-realistic, natural colors, realistic photography, no cartoon, no illustration"
        )
        if name in prompt:   
            with open(char_dir, "rb") as img_fp:
                result = client.images.edit(
                    model="gpt-image-1",
                    image=img_fp,
                    prompt=input_prompt,
                    n=1,
                    size=f"{width}x{height}",
                )
            # 편집 응답은 b64_json 제공됨
            image_b64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)
            with open(save_dir, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {save_dir}")
        else:
            print("(no main character in prompt)")
            result = client.images.generate(
                model="dall-e-3",          # 요청하신 '일반 모델'
                prompt=input_prompt,
                size="1024x1024",
                n=1,
                response_format="b64_json" # ★ 반드시 지정: URL 대신 base64 수신
            )
            # 생성 응답은 기본적으로 url일 수 있으므로 b64_json 강제
            image_b64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_b64)
            with open(save_dir, "wb") as f:
                f.write(image_bytes)
            print(f"Saved (generate): {save_dir}")
        



def gen_dalle_chr_series(width,height,prompt,prev_prompt,background,name,prev_dir,save_dir,char_dir):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    input_prompt = (
        prompt + ", " + background + ", highly detailed, photo-realistic, natural colors, realistic photography, no cartoon, no illustration"
    )
    if name in prompt:
        if name in prev_prompt:
            dir=prev_dir
        else: dir=char_dir
        with open(dir, "rb") as img_fp:
            result = client.images.edit(
            model="gpt-image-1",
            image=img_fp,
            prompt=input_prompt,
            n=1,
            size=f"{width}x{height}",
        )
        # 편집 응답은 b64_json 제공됨
        image_b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)
        with open(save_dir, "wb") as f:
            f.write(image_bytes)
        print(f"캐릭터 등장")
  
    else:
        print("(no main character in prompt)")
        result = client.images.generate(
            model="dall-e-3",          # 요청하신 '일반 모델'
            prompt=input_prompt,
            size="1024x1024",
            n=1,
            response_format="b64_json" # ★ 반드시 지정: URL 대신 base64 수신
        )
        # 생성 응답은 기본적으로 url일 수 있으므로 b64_json 강제
        image_b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_b64)
        with open(save_dir, "wb") as f:
            f.write(image_bytes)
        print("캐릭터 미등장")




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


