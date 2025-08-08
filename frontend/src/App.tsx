import React, { useState } from 'react';

interface JavaScriptAnalysisResult {
  javascript_issues: string[];
  exbuilder6_apis: string[];
  errors: string[];
  execution_flow: string[];
}

function App() {
  const [code, setCode] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState('');
  const [jsAnalysis, setJsAnalysis] = useState<JavaScriptAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [analysisMode, setAnalysisMode] = useState<'review' | 'js-analysis'>('review');

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setCode(e.target.value);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResult('');
    setJsAnalysis(null);
    setError('');
    setLoading(true);
    
    try {
      let res;
      
      if (analysisMode === 'js-analysis') {
        // JavaScript 분석 모드
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
        <label>
          <input
            type="radio"
            name="mode"
            value="js-analysis"
            checked={analysisMode === 'js-analysis'}
            onChange={() => setAnalysisMode('js-analysis')}
          />
          JavaScript 분석
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
          {loading ? '분석 중...' : (analysisMode === 'js-analysis' ? 'JavaScript 분석' : '리뷰 요청')}
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
      {jsAnalysis ? (
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