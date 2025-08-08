#!/usr/bin/env python3
"""
향상된 eXBuilder6 JavaScript 분석기 테스트 스크립트
"""

import asyncio
import sys
import os

# backend 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from enhanced_js_analyzer import PerformanceOptimizedAnalyzer, JavaScriptAnalysisRequest

# 테스트용 JavaScript 코드
TEST_CODE = """
// eXBuilder6 테스트 코드
function onLoad() {
    // Grid 컨트롤 찾기
    var grid = app.lookup("grdMain");
    
    // 잘못된 메서드 호출 (테스트용)
    grid.invalidMethod();
    
    // 올바른 메서드 호출
    grid.addRow();
    grid.setData([{id: 1, name: "Test"}]);
    
    // Button 컨트롤 찾기
    var button = app.lookup("btnSubmit");
    button.setText("제출");
    
    // 보안 위험 코드 (테스트용)
    document.getElementById("content").innerHTML = userInput;
    
    // JSON 파싱 (try-catch 없음)
    var data = JSON.parse(jsonString);
    
    // null 참조 위험
    var element = document.querySelector(".missing");
    element.style.display = "none";
    
    // 비교 연산자 문제
    if (value == null) {
        console.log("null value");
    }
    
    // 무한 루프 위험
    for (;;) {
        // 무한 루프
    }
}

// 이벤트 핸들러
this.onClick = function() {
    var input = app.lookup("ipbName");
    var value = input.getValue();
    
    if (value) {
        app.showMessage("입력값: " + value);
    }
};

// 파일 처리 함수
function handleFileUpload() {
    var fileInput = app.lookup("fipUpload");
    var files = fileInput.files;
    
    if (files.length > 0) {
        var submission = app.lookup("subSubmit");
        submission.addFileParameter("file", files[0]);
    }
}
"""

async def test_enhanced_analyzer():
    """향상된 분석기 테스트"""
    print("🔍 향상된 eXBuilder6 JavaScript 분석기 테스트")
    print("=" * 60)
    
    # 분석기 인스턴스 생성
    analyzer = PerformanceOptimizedAnalyzer()
    
    print("📝 테스트 코드:")
    print("-" * 30)
    print(TEST_CODE)
    print("-" * 30)
    
    # 비동기 분석 실행
    print("\n🚀 분석 시작...")
    results = await analyzer.analyze_async(TEST_CODE)
    
    # 결과 출력
    print("\n📊 분석 결과:")
    print("=" * 60)
    
    # 문법 이슈
    print(f"\n🔧 문법 이슈 ({len(results['syntax'])}개):")
    for issue in results['syntax']:
        print(f"  • [{issue.severity.upper()}] 라인 {issue.line_number}: {issue.message}")
        if issue.suggestion:
            print(f"    💡 제안: {issue.suggestion}")
    
    # API 이슈
    print(f"\n🔌 API 이슈 ({len(results['apis'])}개):")
    for issue in results['apis']:
        print(f"  • [{issue.severity.upper()}] {issue.message}")
        if issue.suggestion:
            print(f"    💡 제안: {issue.suggestion}")
    
    # 오류 이슈
    print(f"\n⚠️ 오류 이슈 ({len(results['errors'])}개):")
    for issue in results['errors']:
        print(f"  • [{issue.severity.upper()}] 라인 {issue.line_number}: {issue.message}")
        if issue.suggestion:
            print(f"    💡 제안: {issue.suggestion}")
    
    # 실행 흐름
    print(f"\n🔄 실행 흐름:")
    for flow in results['flow']:
        print(f"  • {flow}")
    
    # 통계 계산
    all_issues = results['syntax'] + results['apis'] + results['errors']
    critical_count = len([i for i in all_issues if i.severity.value == 'critical'])
    high_count = len([i for i in all_issues if i.severity.value == 'high'])
    medium_count = len([i for i in all_issues if i.severity.value == 'medium'])
    low_count = len([i for i in all_issues if i.severity.value == 'low'])
    
    print(f"\n📈 통계:")
    print(f"  • 총 이슈: {len(all_issues)}개")
    print(f"  • Critical: {critical_count}개")
    print(f"  • High: {high_count}개")
    print(f"  • Medium: {medium_count}개")
    print(f"  • Low: {low_count}개")
    
    # 권장사항
    print(f"\n💡 권장사항:")
    if critical_count > 0:
        print("  • 보안 위험이 있는 코드를 즉시 수정하세요.")
    if high_count > 0:
        print("  • 높은 우선순위 이슈들을 우선적으로 해결하세요.")
    if len(results['syntax']) > 0:
        print("  • 문법 오류를 수정하여 코드 실행을 보장하세요.")
    if len(results['apis']) > 0:
        print("  • eXBuilder6 API 사용법을 확인하고 올바른 메서드를 사용하세요.")
    
    if len(all_issues) == 0:
        print("  • 코드 품질이 양호합니다. 계속해서 좋은 코딩 관례를 유지하세요.")
    
    print("\n✅ 테스트 완료!")

def test_config_manager():
    """설정 관리자 테스트"""
    print("\n🔧 설정 관리자 테스트")
    print("=" * 40)
    
    from enhanced_js_analyzer import ConfigManager
    
    config_manager = ConfigManager()
    
    # API 정보 가져오기
    api_info = config_manager.get_api_info("6.0")
    print(f"eXBuilder6 6.0 API 정보 로드: {'성공' if api_info else '실패'}")
    
    if api_info:
        print(f"  • 지원 컨트롤 수: {len(api_info)}개")
        for control_type in api_info.keys():
            methods_count = len(api_info[control_type].get('methods', []))
            print(f"  • {control_type}: {methods_count}개 메서드")

def test_js_parser():
    """JavaScript 파서 테스트"""
    print("\n🔍 JavaScript 파서 테스트")
    print("=" * 40)
    
    from enhanced_js_analyzer import JavaScriptParser
    
    test_code = """
    // 단일 라인 주석
    var x = 1; // 인라인 주석
    
    /* 
     * 다중 라인 주석
     * 여러 줄에 걸친 주석
     */
    
    var str = "문자열 내부의 // 주석은 무시됨";
    var str2 = '문자열 내부의 /* 주석 */ 도 무시됨';
    
    function test() {
        // 함수 내부 주석
        return "test";
    }
    """
    
    parser = JavaScriptParser()
    cleaned_code = parser.clean_code(test_code)
    
    print("원본 코드:")
    print(test_code)
    print("\n정리된 코드:")
    print(cleaned_code)
    
    # 주석이 제거되었는지 확인
    if "//" not in cleaned_code and "/*" not in cleaned_code:
        print("✅ 주석 제거 성공")
    else:
        print("❌ 주석 제거 실패")

def test_api_validator():
    """API 검증기 테스트"""
    print("\n🔌 API 검증기 테스트")
    print("=" * 40)
    
    from enhanced_js_analyzer import EXBuilder6APIValidator, ConfigManager
    
    config_manager = ConfigManager()
    validator = EXBuilder6APIValidator(config_manager)
    
    # 컨트롤 타입 식별 테스트
    test_controls = [
        "grdMain",
        "btnSubmit", 
        "cmbCategory",
        "cbxAgree",
        "ipbName",
        "grd123",
        "btn456",
        "unknownControl"
    ]
    
    print("컨트롤 타입 식별:")
    for control_id in test_controls:
        control_type = validator.identify_control_type(control_id)
        print(f"  • {control_id} → {control_type}")
    
    # API 사용 검증 테스트
    print("\nAPI 사용 검증:")
    test_cases = [
        ("grd", "addRow", "grd"),
        ("grd", "invalidMethod", "grd"),
        ("btn", "setText", "btn"),
        ("btn", "invalidMethod", "btn")
    ]
    
    for control_type, method_name, var_name in test_cases:
        issues = validator.validate_api_usage(var_name, method_name, control_type)
        if issues:
            print(f"  • {control_type}.{method_name}(): {issues[0].message}")
        else:
            print(f"  • {control_type}.{method_name}(): ✅ 유효한 API")

async def main():
    """메인 테스트 함수"""
    print("🚀 향상된 eXBuilder6 JavaScript 분석기 종합 테스트")
    print("=" * 80)
    
    try:
        # 각 테스트 실행
        test_config_manager()
        test_js_parser()
        test_api_validator()
        await test_enhanced_analyzer()
        
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
