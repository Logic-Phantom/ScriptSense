import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

def request_llm(prompt: str, mode: str = None) -> str:
    # mode: 'openai' or 'lmstudio' (기본: 환경변수 LLM_MODE, 없으면 openai)
    mode = mode or os.getenv("LLM_MODE", "openai").lower()
    if mode == "lmstudio":
        url = "http://localhost:1234/v1/chat/completions"
        # 프롬프트 길이 제한 (예: 2000자)
        if len(prompt) > 2000:
            return "[ERROR] 프롬프트가 너무 깁니다. 2000자 이하로 줄여주세요."
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['message']['content'].strip()
            else:
                return f"[ERROR] LLM 응답 포맷 오류: {data}"
        except requests.exceptions.Timeout:
            return "[ERROR] LLM 요청 실패 (LM Studio): 응답이 120초 내에 오지 않았습니다.\n- LM Studio에 모델이 로드되어 있는지 확인하세요.\n- 너무 큰 모델/긴 프롬프트/PC 사양 문제일 수 있습니다.\n- LM Studio에서 직접 테스트해보세요."
        except Exception as e:
            return f"[ERROR] LLM 요청 실패 (LM Studio): {e}\n(응답 내용: {getattr(e, 'response', None)})"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "[ERROR] OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다."
        client = openai.OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ERROR] LLM 요청 실패 (OpenAI): {e}"