import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

def request_llm_fast(prompt: str, mode: str = None) -> str:
    """빠른 응답을 위한 LLM 요청 (토큰 수 제한)"""
    return request_llm(prompt, mode, max_tokens=512)

def request_llm(prompt: str, mode: str = None, max_tokens: int = 1024) -> str:
    # mode: 'openai' or 'lmstudio' (기본: 환경변수 LLM_MODE, 없으면 openai)
    mode = mode or os.getenv("LLM_MODE", "openai").lower()
    print(f"[LOG] LLM Mode: {mode}")
    if mode == "lmstudio":
        url = "http://localhost:1234/v1/chat/completions"
        # 프롬프트 길이 제한 (예: 2000자)
        if len(prompt) > 2000:
            return "[ERROR] 프롬프트가 너무 깁니다. 2000자 이하로 줄여주세요."
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": False,  # 스트리밍 비활성화
            "top_p": 0.9,     # 토큰 선택 최적화
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        try:
            response = requests.post(url, json=payload, timeout=300)  # 5분으로 증가
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and data['choices']:
                return data['choices'][0]['message']['content'].strip()
            else:
                return f"[ERROR] LLM 응답 포맷 오류: {data}"
        except requests.exceptions.Timeout:
            return "[ERROR] LLM 요청 실패 (LM Studio): 응답이 5분 내에 오지 않았습니다.\n해결 방법:\n1. LM Studio에서 더 빠른 모델 사용 (7B 이하 권장)\n2. GPU 가속이 활성화되어 있는지 확인\n3. max_tokens를 512 이하로 줄이기\n4. 프롬프트 길이 단축\n5. PC 사양 업그레이드 고려"
        except requests.exceptions.ConnectionError as e:
            return f"[ERROR] LM Studio 연결 실패: {e}\n\n해결 방법:\n1. LM Studio가 실행 중인지 확인하세요\n2. LM Studio에서 모델이 로드되어 있는지 확인하세요\n3. LM Studio가 포트 1234에서 실행 중인지 확인하세요\n4. 또는 환경변수 LLM_MODE=openai로 설정하여 OpenAI API를 사용하세요"
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
                max_tokens=max_tokens,
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ERROR] LLM 요청 실패 (OpenAI): {e}"