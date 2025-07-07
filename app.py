# 🔮 전생 뽑기: 이름 입력 → GPT-4o 전생 설정 + 이미지 생성 Streamlit 앱

import streamlit as st
import openai
import json

# ✅ OpenAI API 키 설정
import os
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI API KEY ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# 📌 GPT: 전생 캐릭터 생성 함수
# -----------------------------
def generate_character_from_name(name: str) -> dict:
    system_prompt = f"""
    당신은 이름 하나만 보고 전생 캐릭터 정보를 무작위로 창작하는 AI입니다.

    다음 조건을 지키세요:
    - "시대"는 반드시 현재보다 과거여야 합니다 (미래 불가).
    - "공간"은 전 세계 어디든 무작위일 수 있으며, 한국일 필요는 없습니다.

    입력:
    이름: {name}

    출력 형식은 아래와 같습니다 (JSON):

    {{
      "시대": "예: 15세기 이탈리아",
      "성별": "여성 / 남성 / 중성",
      "직업": "예: 궁중 서예가",
      "특징": "예: 비단 한복을 입고 서재에 앉아 있는 모습",
      "성격 키워드": "예: 차분하고 집중력이 강한 성격"
    }}
    """

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{name}의 전생 캐릭터를 알려줘."}
        ],
        temperature=1.0
    )

    content = response.choices[0].message.content
    try:
        character = json.loads(content)
    except json.JSONDecodeError:
        st.error("❌ GPT 응답을 JSON으로 파싱할 수 없습니다.\n응답 내용: " + content)
        return None

    return character

# -----------------------------
# 🖼 이미지 프롬프트 생성 함수 (클래식 초상화 스타일)
# -----------------------------
def generate_image_prompt(character: dict) -> str:
    era = character.get("시대", "a past era")
    gender = character.get("성별", "a person")
    job = character.get("직업", "a historical figure")
    feature = character.get("특징", "")

    gender_en = {
        "남성": "male",
        "여성": "female",
        "중성": "androgynous",
    }.get(gender, "person")

    prompt = (
        f"A {gender_en} {job} from {era}, {feature.lower()}, "
        f"posed for a formal portrait in classical oil painting style, "
        f"neutral background, soft studio lighting, rich historical detail."
    )
    return prompt

# -----------------------------
# 🎨 GPT-4o 이미지 생성 API 호출
# -----------------------------
def generate_image_from_prompt(prompt: str) -> str:
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="standard"
    )
    return response.data[0].url

# -----------------------------
# 🖥 Streamlit UI
# -----------------------------
st.set_page_config(page_title="전생 뽑기", layout="centered")
st.title("🔮 전생 뽑기")
st.caption("이름만 입력하면 당신의 전생이 뽑힙니다!")

name = st.text_input("당신의 이름을 입력하세요", max_chars=20)

if st.button("전생 뽑기"):
    if not name:
        st.warning("이름을 입력해 주세요!")
    else:
        with st.spinner("전생을 불러오는 중..."):
            character = generate_character_from_name(name)

            if character:
                prompt = generate_image_prompt(character)
                image_url = generate_image_from_prompt(prompt)

                st.subheader(f"✨ {name}님의 전생은...")

                # 카드 형식으로 이미지 + 프로필 나란히 출력
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(image_url, caption="AI가 생성한 전생 이미지", use_container_width=True)
                with col2:
                    st.markdown(
                        f"""
                        <div style="background-color:#f8f9fa; border-radius:12px; padding:24px; box-shadow:0 2px 8px #ddd;">
                            <h4 style="margin-top:0;">전생 프로필</h4>
                            <ul style="list-style:none; padding-left:0;">
                                <li><b>시대:</b> {character['시대']}</li>
                                <li><b>직업:</b> {character['직업']}</li>
                                <li><b>특징:</b> {character['특징']}</li>
                                <li><b>성격:</b> {character['성격 키워드']}</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("---")
                st.markdown("📤 친구에게 전생 사이트 공유하기")
                share_url = f"https://pastlife.streamlit.app"
                st.code(share_url)
                st.caption("👆 위 링크를 복사해 친구에게 공유하세요!")

                st.button("🔁 다시 뽑기")