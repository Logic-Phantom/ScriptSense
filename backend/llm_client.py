import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

def request_llm(prompt: str, mode: str = None) -> str:
    # mode: 'openai' or 'lmstudio' (기본: 환경변수 LLM_MODE, 없으면 openai)
    mode = mode or os.getenv("LLM_MODE", "openai").lower()
    if mode == "lmstudio":
        url = "http://localhost:1234/v1/chat"
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1024,
            "temperature": 0.2
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"[ERROR] LLM 요청 실패 (LM Studio): {e}"
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