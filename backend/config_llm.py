#!/usr/bin/env python3
"""
LLM Configuration Helper Script

이 스크립트를 사용하여 LLM 모드를 쉽게 전환할 수 있습니다.
"""

import os
import sys

def set_environment_variable(key, value):
    """환경변수 설정 (현재 세션만 유효)"""
    os.environ[key] = value
    print(f"✅ {key}={value} 설정됨 (현재 세션만 유효)")

def show_current_config():
    """현재 설정 표시"""
    print("=== 현재 LLM 설정 ===")
    llm_mode = os.getenv("LLM_MODE", "openai")
    openai_key = os.getenv("OPENAI_API_KEY", "설정되지 않음")
    
    print(f"LLM_MODE: {llm_mode}")
    print(f"OPENAI_API_KEY: {'설정됨' if openai_key != '설정되지 않음' else '설정되지 않음'}")

def switch_to_openai():
    """OpenAI 모드로 전환"""
    api_key = input("OpenAI API Key를 입력하세요: ").strip()
    if api_key:
        set_environment_variable("LLM_MODE", "openai")
        set_environment_variable("OPENAI_API_KEY", api_key)
        print("🔄 OpenAI 모드로 전환되었습니다.")
    else:
        print("❌ API Key가 입력되지 않았습니다.")

def switch_to_lmstudio():
    """LM Studio 모드로 전환"""
    set_environment_variable("LLM_MODE", "lmstudio")
    print("🔄 LM Studio 모드로 전환되었습니다.")
    print("\n⚠️  주의사항:")
    print("1. LM Studio가 실행되어 있어야 합니다")
    print("2. 모델이 로드되어 있어야 합니다")
    print("3. 포트 1234에서 서버가 실행되어야 합니다")

def main():
    print("🤖 ScriptSense LLM 설정 도구")
    print("=" * 30)
    
    while True:
        show_current_config()
        print("\n옵션을 선택하세요:")
        print("1. OpenAI로 전환")
        print("2. LM Studio로 전환")
        print("3. 현재 설정 확인")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            switch_to_openai()
        elif choice == "2":
            switch_to_lmstudio()
        elif choice == "3":
            continue
        elif choice == "4":
            print("👋 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다.")
        
        print("\n" + "-" * 30)

if __name__ == "__main__":
    main()
