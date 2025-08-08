import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

def request_llm_fast(prompt: str, mode: str = None) -> str:
    """빠른 응답을 위한 LLM 요청 (토큰 수 제한)"""
    return request_llm(prompt, mode, max_tokens=1024)  # 256 → 1024로 증가

def request_llm(prompt: str, mode: str = None, max_tokens: int = 2048) -> str:  # 1024 → 2048로 증가
    # mode: 'openai' or 'lmstudio' (기본: 환경변수 LLM_MODE, 없으면 openai)
    mode = mode or os.getenv("LLM_MODE", "openai").lower()
    print(f"[LOG] LLM Mode: {mode}")
    if mode == "lmstudio":
        url = "http://localhost:1234/v1/chat/completions"
        # 프롬프트 길이 제한 (토큰 기반으로 계산)
        # 대략적으로 1토큰 = 4글자로 계산하여 3500 토큰 이하로 제한
        estimated_tokens = len(prompt) // 4
        if estimated_tokens > 3500:
            return f"[ERROR] 프롬프트가 너무 깁니다. (예상 토큰: {estimated_tokens}, 제한: 3500)\n해결 방법:\n1. 코드를 더 작은 단위로 나누어 분석\n2. 불필요한 주석 제거\n3. LM Studio에서 더 큰 컨텍스트 모델 사용"
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "stream": False
        }
        try:
            print(f"[LOG] Sending request to LM Studio: {url}")
            print(f"[LOG] Payload: {payload}")
            response = requests.post(url, json=payload, timeout=300)  # 5분으로 증가
            print(f"[LOG] Response status: {response.status_code}")
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
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                try:
                    error_detail = e.response.json()
                    return f"[ERROR] LM Studio 400 오류: {error_detail}\n\n해결 방법:\n1. LM Studio에서 모델이 제대로 로드되었는지 확인\n2. 프롬프트 길이를 줄여보세요\n3. max_tokens를 512 이하로 줄여보세요\n4. LM Studio 서버를 재시작해보세요"
                except:
                    return f"[ERROR] LM Studio 400 오류: {e}\n\n해결 방법:\n1. LM Studio에서 모델이 제대로 로드되었는지 확인\n2. 프롬프트 길이를 줄여보세요\n3. max_tokens를 512 이하로 줄여보세요\n4. LM Studio 서버를 재시작해보세요"
            else:
                return f"[ERROR] LM Studio HTTP 오류: {e}"
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