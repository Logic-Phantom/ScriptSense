import React, { useState } from 'react';

interface AnalysisIssue {
  category: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  line_number?: number;
  suggestion: string;
}

interface EnhancedJavaScriptAnalysisResult {
  issues: AnalysisIssue[];
  execution_flow: string[];
  llm_analysis?: string;
  statistics?: {
    total_issues: number;
    critical_issues: number;
    high_priority_issues: number;
    medium_priority_issues: number;
    low_priority_issues: number;
  };
  recommendations?: string[];
}

interface JavaScriptAnalysisResult {
  javascript_issues: string[];
  exbuilder6_apis: string[];
  errors: string[];
  execution_flow: string[];
  llm_analysis?: string;
}

function App() {
  const [code, setCode] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState('');
  const [jsAnalysis, setJsAnalysis] = useState<JavaScriptAnalysisResult | null>(null);
  const [enhancedAnalysis, setEnhancedAnalysis] = useState<EnhancedJavaScriptAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisMode, setAnalysisMode] = useState<'review' | 'js-analysis' | 'enhanced-js-analysis'>('review');

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setCode(e.target.value);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResult('');
    setJsAnalysis(null);
    setEnhancedAnalysis(null);
    setError('');
    setLoading(true);
    
    try {
      let res;
      
      if (analysisMode === 'enhanced-js-analysis') {
        // 향상된 JavaScript 분석 모드 (LM Studio 포함)
        if (file) {
          const formData = new FormData();
          formData.append('file', file);
          res = await fetch('/api/enhanced-js/analyze/file', {
            method: 'POST',
            body: formData,
          });
        } else if (code.trim()) {
          res = await fetch('/api/enhanced-js/analyze/detailed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, fast_mode: false }),
          });
        } else {
          setError('코드를 입력하거나 파일을 업로드하세요.');
          setLoading(false);
          return;
        }
        
        if (!res.ok) {
          const err = await res.json();
          setError(err.detail || '서버 오류');
        } else {
          const data = await res.json();
          setEnhancedAnalysis(data);
        }
      } else if (analysisMode === 'js-analysis') {
        // 기존 JavaScript 분석 모드
        if (file) {
          const formData = new FormData();
          formData.append('file', file);
          res = await fetch('/api/js/analyze/file', {
            method: 'POST',
            body: formData,
          });
        } else if (code.trim()) {
          res = await fetch('/api/js/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, fast_mode: false }),
          });
        } else {
          setError('코드를 입력하거나 파일을 업로드하세요.');
          setLoading(false);
          return;
        }
        
        if (!res.ok) {
          const err = await res.json();
          setError(err.detail || '서버 오류');
        } else {
          const data = await res.json();
          setJsAnalysis(data);
        }
      } else {
        // 기존 리뷰 모드
        if (file) {
          const formData = new FormData();
          formData.append('file', file);
          res = await fetch('/api/review/file', {
            method: 'POST',
            body: formData,
          });
        } else if (code.trim()) {
          res = await fetch('/api/review/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
          });
        } else {
          setError('코드를 입력하거나 파일을 업로드하세요.');
          setLoading(false);
          return;
        }
        
        if (!res.ok) {
          const err = await res.json();
          setError(err.detail || '서버 오류');
        } else {
          const data = await res.json();
          setResult(data.result);
        }
      }
    } catch (e) {
      setError('네트워크 오류 또는 서버 연결 실패');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return '#dc3545';
      case 'HIGH': return '#fd7e14';
      case 'MEDIUM': return '#ffc107';
      case 'LOW': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH': return '#dc3545';
      case 'MEDIUM': return '#ffc107';
      case 'LOW': return '#28a745';
      default: return '#6c757d';
    }
  };

  const formatEnhancedAnalysis = (analysis: EnhancedJavaScriptAnalysisResult) => {
    let output = '';

    // 요약 정보 (안전한 처리)
    if (analysis.statistics) {
      output += '**📊 분석 요약:**\n';
      output += `- 총 문제점: ${analysis.statistics.total_issues || 0}개\n`;
      output += `- 🔴 Critical: ${analysis.statistics.critical_issues || 0}개\n`;
      output += `- 🟠 High: ${analysis.statistics.high_priority_issues || 0}개\n`;
      output += `- 🟡 Medium: ${analysis.statistics.medium_priority_issues || 0}개\n`;
      output += `- 🟢 Low: ${analysis.statistics.low_priority_issues || 0}개\n\n`;
    } else {
      output += '**📊 분석 요약:**\n';
      output += `- 총 문제점: ${analysis.issues?.length || 0}개\n\n`;
    }

    // 문제점들을 심각도별로 그룹화
    const issuesBySeverity = analysis.issues.reduce((acc, issue) => {
      if (!acc[issue.severity]) acc[issue.severity] = [];
      acc[issue.severity].push(issue);
      return acc;
    }, {} as Record<string, AnalysisIssue[]>);

    // Critical부터 Low 순으로 정렬 (소문자로 매칭)
    const severityOrder = ['critical', 'high', 'medium', 'low'];
    
    severityOrder.forEach(severity => {
      if (issuesBySeverity[severity] && issuesBySeverity[severity].length > 0) {
        const severityEmoji = severity === 'critical' ? '🔴' : 
                             severity === 'high' ? '🟠' : 
                             severity === 'medium' ? '🟡' : '🟢';
        const severityDisplay = severity.toUpperCase();
        
        output += `**${severityEmoji} ${severityDisplay} 심각도 문제점 (${issuesBySeverity[severity].length}개):**\n`;
        
        issuesBySeverity[severity].forEach((issue, index) => {
          const lineInfo = issue.line_number ? ` (라인 ${issue.line_number})` : '';
          const priorityInfo = `[우선순위: ${issue.priority || 'N/A'}]`;
          
          output += `${index + 1}. **${issue.category}**${lineInfo} ${priorityInfo}\n`;
          output += `   - 문제: ${issue.message}\n`;
          output += `   - 제안: ${issue.suggestion || '구체적인 제안사항이 없습니다.'}\n\n`;
        });
      }
    });

    // 문제점이 없을 때 메시지
    if (analysis.issues.length === 0) {
      output += '**✅ 발견된 문제점 없음**\n\n';
    }

    // 실행 흐름
    if (analysis.execution_flow.length > 0) {
      output += '**🔄 실행 흐름:**\n';
      analysis.execution_flow.forEach((step, index) => {
        output += `${index + 1}. ${step}\n`;
      });
      output += '\n';
    }

    // 권장사항 (있는 경우)
    if (analysis.recommendations && analysis.recommendations.length > 0) {
      output += '**💡 권장사항:**\n';
      analysis.recommendations.forEach((rec, index) => {
        output += `${index + 1}. ${rec}\n`;
      });
      output += '\n';
    }

    // LM Studio 분석 결과 (있는 경우)
    if (analysis.llm_analysis) {
      output += '**🤖 LM Studio 상세 분석:**\n';
      output += analysis.llm_analysis;
    }

    return output;
  };

  const formatJsAnalysis = (analysis: JavaScriptAnalysisResult) => {
    let output = '';

    // 1. JavaScript 문제점
    output += '**1. JavaScript 문법/로직 문제점:**\n';
    if (analysis.javascript_issues.length === 0) {
      output += '- 발견된 문제점 없음\n';
    } else {
      analysis.javascript_issues.forEach(issue => {
        output += `- ${issue}\n`;
      });
    }

    // 2. eXBuilder6 API 사용 여부
    output += '\n**2. eXBuilder6 API 사용 여부:**\n';
    if (analysis.exbuilder6_apis.length === 0) {
      output += '- eXBuilder6 API 사용 안함\n';
    } else {
      output += '- 사용된 eXBuilder6 API:\n';
      analysis.exbuilder6_apis.forEach(api => {
        output += `  - ${api}\n`;
      });
    }

    // 3. 오류 검사
    output += '\n**3. 오류 검사:**\n';
    if (analysis.errors.length === 0) {
      output += '- 발견된 오류 없음\n';
    } else {
      analysis.errors.forEach(error => {
        output += `- ${error}\n`;
      });
    }

    // 4. 실행 흐름
    output += '\n**4. 실행 흐름:**\n';
    analysis.execution_flow.forEach(step => {
      output += `- ${step}\n`;
    });

    // 5. LM Studio 분석 결과 (있는 경우)
    if (analysis.llm_analysis) {
      output += '\n**5. LM Studio 상세 분석:**\n';
      output += analysis.llm_analysis;
    }

    return output;
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 32 }}>
      <h1>ScriptSense: JS 코드 자동 리뷰 & 분석</h1>
      
      {/* 분석 모드 선택 */}
      <div style={{ marginBottom: 20 }}>
        <label style={{ marginRight: 20 }}>
          <input
            type="radio"
            name="mode"
            value="review"
            checked={analysisMode === 'review'}
            onChange={() => setAnalysisMode('review')}
          />
          일반 리뷰
        </label>
        <label style={{ marginRight: 20 }}>
          <input
            type="radio"
            name="mode"
            value="js-analysis"
            checked={analysisMode === 'js-analysis'}
            onChange={() => setAnalysisMode('js-analysis')}
          />
          JavaScript 분석
        </label>
        <label>
          <input
            type="radio"
            name="mode"
            value="enhanced-js-analysis"
            checked={analysisMode === 'enhanced-js-analysis'}
            onChange={() => setAnalysisMode('enhanced-js-analysis')}
          />
          향상된 JavaScript 분석 (LM Studio 포함)
        </label>
      </div>

      <form onSubmit={handleSubmit}>
        <textarea
          value={code}
          onChange={handleCodeChange}
          placeholder="여기에 JavaScript 코드를 입력하세요"
          rows={12}
          style={{ 
            width: '100%', 
            fontFamily: 'monospace', 
            marginBottom: 16,
            fontSize: '14px',
            padding: '12px'
          }}
        />
        <div>
          <input type="file" accept=".js" onChange={handleFileChange} />
        </div>
        <button 
          type="submit" 
          style={{ 
            marginTop: 16, 
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }} 
          disabled={loading}
        >
          {loading ? '분석 중...' : 
           analysisMode === 'enhanced-js-analysis' ? '향상된 JavaScript 분석 (LM Studio)' :
           analysisMode === 'js-analysis' ? 'JavaScript 분석' : '리뷰 요청'}
        </button>
      </form>
      
      {error && (
        <div style={{ color: 'red', marginTop: 16, padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '4px' }}>
          {error}
        </div>
      )}
      
      <hr style={{ margin: '32px 0' }} />
      
      {/* 결과 표시 */}
      <h2>분석 결과</h2>
      {enhancedAnalysis ? (
        <pre style={{ 
          background: '#f8f9fa', 
          padding: 20, 
          minHeight: 200,
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          {formatEnhancedAnalysis(enhancedAnalysis)}
        </pre>
      ) : jsAnalysis ? (
        <pre style={{ 
          background: '#f8f9fa', 
          padding: 20, 
          minHeight: 200,
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          {formatJsAnalysis(jsAnalysis)}
        </pre>
      ) : result && (
        <pre style={{ 
          background: '#f8f9fa', 
          padding: 20, 
          minHeight: 200,
          border: '1px solid #dee2e6',
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          {result}
        </pre>
      )}
    </div>
  );
}

export default App;