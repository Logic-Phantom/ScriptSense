const fs = require('fs');
const path = require('path');

class JavaScriptAnalyzer {
    constructor() {
        this.exBuilder6APIs = [
            'this.form', 'this.grid', 'this.tree', 'this.combo', 'this.button',
            'this.onLoad', 'this.onClick', 'this.onChange', 'this.onSelect',
            'this.getValue', 'this.setValue', 'this.getData', 'this.setData',
            'this.addRow', 'this.deleteRow', 'this.updateRow',
            'this.showMessage', 'this.showConfirm', 'this.showAlert',
            'this.openPopup', 'this.closePopup', 'this.getParent',
            'this.getChild', 'this.getSibling', 'this.getRoot',
            'this.getSelected', 'this.getChecked', 'this.getExpanded',
            'this.setSelected', 'this.setChecked', 'this.setExpanded',
            'this.refresh', 'this.reload', 'this.clear',
            'this.enable', 'this.disable', 'this.show', 'this.hide',
            'this.focus', 'this.blur', 'this.scrollTo', 'this.scrollIntoView'
        ];
    }

    analyzeCode(code) {
        const result = {
            javascriptIssues: this.checkJavaScriptIssues(code),
            exBuilder6APIs: this.checkExBuilder6APIs(code),
            errors: this.checkErrors(code),
            executionFlow: this.analyzeExecutionFlow(code)
        };
        
        return this.formatResult(result);
    }

    checkJavaScriptIssues(code) {
        const issues = [];
        
        // 기본적인 JavaScript 문법 검사
        try {
            new Function(code);
        } catch (e) {
            issues.push(`문법 오류: ${e.message}`);
        }

        // 일반적인 문제점들 검사
        const patterns = [
            { pattern: /var\s+\w+\s*=\s*undefined/, message: 'undefined 할당은 불필요합니다' },
            { pattern: /==\s*null/, message: 'null 비교시 === 사용을 권장합니다' },
            { pattern: /==\s*undefined/, message: 'undefined 비교시 === 사용을 권장합니다' },
            { pattern: /console\.log\(/, message: 'console.log는 프로덕션에서 제거해야 합니다' },
            { pattern: /eval\(/, message: 'eval() 사용은 보안상 위험합니다' },
            { pattern: /setTimeout\([^,]+,\s*0\)/, message: 'setTimeout(,0) 대신 setImmediate 사용을 고려하세요' }
        ];

        patterns.forEach(({ pattern, message }) => {
            if (pattern.test(code)) {
                issues.push(message);
            }
        });

        return issues;
    }

    checkExBuilder6APIs(code) {
        const foundAPIs = [];
        
        this.exBuilder6APIs.forEach(api => {
            if (code.includes(api)) {
                foundAPIs.push(api);
            }
        });

        return foundAPIs;
    }

    checkErrors(code) {
        const errors = [];
        
        // 잠재적 오류 패턴 검사
        const errorPatterns = [
            { pattern: /\.getElementById\([^)]*\)\./, message: 'getElementById 결과가 null일 수 있습니다' },
            { pattern: /\.querySelector\([^)]*\)\./, message: 'querySelector 결과가 null일 수 있습니다' },
            { pattern: /\.innerHTML\s*=/, message: 'innerHTML 사용시 XSS 위험이 있습니다' },
            { pattern: /JSON\.parse\([^)]*\)/, message: 'JSON.parse는 try-catch로 감싸야 합니다' },
            { pattern: /\.split\([^)]*\)\[/, message: 'split 결과가 빈 배열일 수 있습니다' }
        ];

        errorPatterns.forEach(({ pattern, message }) => {
            if (pattern.test(code)) {
                errors.push(message);
            }
        });

        return errors;
    }

    analyzeExecutionFlow(code) {
        const flow = [];
        
        // 함수 정의 찾기
        const functionMatches = code.match(/function\s+(\w+)\s*\(/g);
        if (functionMatches) {
            flow.push('함수 정의: ' + functionMatches.map(f => f.replace('function ', '').replace('(', '')).join(', '));
        }

        // 이벤트 리스너 찾기
        const eventMatches = code.match(/\.addEventListener\([^)]+\)/g);
        if (eventMatches) {
            flow.push('이벤트 리스너: ' + eventMatches.join(', '));
        }

        // 비동기 작업 찾기
        const asyncMatches = code.match(/(setTimeout|setInterval|fetch|Promise|async|await)/g);
        if (asyncMatches) {
            flow.push('비동기 작업: ' + [...new Set(asyncMatches)].join(', '));
        }

        // 조건문 찾기
        const conditionalMatches = code.match(/(if|else|switch|case)/g);
        if (conditionalMatches) {
            flow.push('조건부 실행: ' + [...new Set(conditionalMatches)].join(', '));
        }

        // 반복문 찾기
        const loopMatches = code.match(/(for|while|do)/g);
        if (loopMatches) {
            flow.push('반복 실행: ' + [...new Set(loopMatches)].join(', '));
        }

        return flow.length > 0 ? flow : ['순차적 실행'];
    }

    formatResult(result) {
        let output = '';

        // 1. JavaScript 문제점
        output += '**1. JavaScript 문법/로직 문제점:**\n';
        if (result.javascriptIssues.length === 0) {
            output += '- 발견된 문제점 없음\n';
        } else {
            result.javascriptIssues.forEach(issue => {
                output += `- ${issue}\n`;
            });
        }

        // 2. eXBuilder6 API 사용 여부
        output += '\n**2. eXBuilder6 API 사용 여부:**\n';
        if (result.exBuilder6APIs.length === 0) {
            output += '- eXBuilder6 API 사용 안함\n';
        } else {
            output += '- 사용된 eXBuilder6 API:\n';
            result.exBuilder6APIs.forEach(api => {
                output += `  - ${api}\n`;
            });
        }

        // 3. 오류 검사
        output += '\n**3. 오류 검사:**\n';
        if (result.errors.length === 0) {
            output += '- 발견된 오류 없음\n';
        } else {
            result.errors.forEach(error => {
                output += `- ${error}\n`;
            });
        }

        // 4. 실행 흐름
        output += '\n**4. 실행 흐름:**\n';
        result.executionFlow.forEach(step => {
            output += `- ${step}\n`;
        });

        return output;
    }
}

// 사용 예시
function analyzeJavaScriptCode(code) {
    const analyzer = new JavaScriptAnalyzer();
    return analyzer.analyzeCode(code);
}

// 파일에서 읽어서 분석하는 함수
function analyzeJavaScriptFile(filePath) {
    try {
        const code = fs.readFileSync(filePath, 'utf8');
        return analyzeJavaScriptCode(code);
    } catch (error) {
        return `파일 읽기 오류: ${error.message}`;
    }
}

// CLI에서 사용할 수 있도록 export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { JavaScriptAnalyzer, analyzeJavaScriptCode, analyzeJavaScriptFile };
}

// 브라우저에서 사용할 수 있도록 전역 함수로 등록
if (typeof window !== 'undefined') {
    window.analyzeJavaScriptCode = analyzeJavaScriptCode;
}

console.log('JavaScript 코드 분석 도구가 로드되었습니다.');
console.log('사용법: analyzeJavaScriptCode(yourCode)');
