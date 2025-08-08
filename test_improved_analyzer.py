#!/usr/bin/env python3
"""
개선된 JavaScript 분석기 테스트 스크립트

이 스크립트는 개선된 JavaScript 분석 기능을 테스트합니다:
1. 정확한 라인 위치 표시
2. eXBuilder6 API 검증 개선
3. 프로세스 중심 실행 흐름 분석
4. 대용량 파일 배치 처리
"""

import requests
import json
import time

# 테스트용 JavaScript 코드
test_code = """
function onFi1ValueChange() {
    const fileinput1 = app.lookup("fi1");
    const vaFiles = fileinput1.files;
    const submit = app.lookup("submission1");
    
    for (let i = 0; i < vaFiles.length; i++) {
        const voFile = vaFiles[i];
        submit.addFileParameter("file" + i, voFile);
    }
}

function testFunction() {
    const grid = app.lookup("grd1");
    grid.addRow();
    grid.setValue("column1", "test");
    
    const button = app.lookup("btn1");
    button.setText("Click me");
    
    if (true) {
        console.log("test");
    }
}
"""

def test_basic_analysis():
    """기본 분석 테스트"""
    print("=== 기본 분석 테스트 ===")
    
    url = "http://localhost:8000/api/js/analyze"
    data = {
        "code": test_code,
        "fast_mode": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"분석 시간: {end_time - start_time:.2f}초")
            print("\n1. JavaScript 문법/로직 문제점:")
            for issue in result.get('javascript_issues', []):
                print(f"   - {issue}")
            
            print("\n2. eXBuilder6 API 사용 여부:")
            for api in result.get('exbuilder6_apis', []):
                print(f"   - {api}")
            
            print("\n3. 오류 검사:")
            for error in result.get('errors', []):
                print(f"   - {error}")
            
            print("\n4. 실행 흐름:")
            for flow in result.get('execution_flow', []):
                print(f"   - {flow}")
        else:
            print(f"오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")

def test_batch_analysis():
    """배치 분석 테스트"""
    print("\n=== 배치 분석 테스트 ===")
    
    # 대용량 테스트 코드 생성
    large_code = test_code * 100  # 약 3000줄
    
    url = "http://localhost:8000/api/js/analyze/batch"
    data = {
        "code": large_code,
        "fast_mode": True
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"배치 분석 시간: {end_time - start_time:.2f}초")
            print(f"총 코드 길이: {result.get('total_code_length', 0)}")
            print(f"배치 개수: {result.get('batch_count', 0)}")
            print(f"배치 크기: {result.get('batch_size', 0)}")
            
            combined = result.get('combined_result', {})
            print(f"\n통합된 결과:")
            print(f"- 문법 문제: {len(combined.get('javascript_issues', []))}개")
            print(f"- API 문제: {len(combined.get('exbuilder6_apis', []))}개")
            print(f"- 오류: {len(combined.get('errors', []))}개")
            print(f"- 실행 흐름: {len(combined.get('execution_flow', []))}개")
        else:
            print(f"오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"배치 테스트 중 오류 발생: {e}")

def test_detailed_analysis():
    """상세 분석 테스트"""
    print("\n=== 상세 분석 테스트 ===")
    
    url = "http://localhost:8000/api/js/analyze/detailed"
    data = {
        "code": test_code,
        "fast_mode": False
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"상세 분석 시간: {end_time - start_time:.2f}초")
            
            basic = result.get('basic_analysis', {})
            llm = result.get('llm_analysis', {})
            
            print(f"\n기본 분석 결과:")
            print(f"- 문법 문제: {len(basic.get('javascript_issues', []))}개")
            print(f"- API 문제: {len(basic.get('exbuilder6_apis', []))}개")
            
            print(f"\nLLM 분석 결과:")
            if isinstance(llm, dict) and 'llm_analysis' in llm:
                print("LLM 분석이 성공적으로 수행되었습니다.")
            else:
                print("LLM 분석 결과를 확인할 수 없습니다.")
        else:
            print(f"오류: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"상세 테스트 중 오류 발생: {e}")

def main():
    """메인 테스트 함수"""
    print("개선된 JavaScript 분석기 테스트 시작")
    print("=" * 50)
    
    # 서버 상태 확인
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("서버가 정상적으로 실행 중입니다.")
        else:
            print("서버에 연결할 수 없습니다. 서버를 먼저 실행해주세요.")
            return
    except:
        print("서버에 연결할 수 없습니다. 서버를 먼저 실행해주세요.")
        return
    
    # 테스트 실행
    test_basic_analysis()
    test_batch_analysis()
    test_detailed_analysis()
    
    print("\n" + "=" * 50)
    print("테스트 완료")

if __name__ == "__main__":
    main()
