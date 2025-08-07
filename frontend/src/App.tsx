import React, { useState } from 'react';

function App() {
  const [code, setCode] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => setCode(e.target.value);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setResult('');
    setError('');
    setLoading(true);
    try  {
      let res;
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
    } catch (e) {
      setError('네트워크 오류 또는 서버 연결 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 700, margin: '0 auto', padding: 32 }}>
      <h1>ScriptSense: JS 코드 자동 리뷰 & 흐름 요약</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={code}
          onChange={handleCodeChange}
          placeholder="여기에 JS 코드를 입력하세요"
          rows={10}
          style={{ width: '100%', fontFamily: 'monospace', marginBottom: 16 }}
        />
        <div>
          <input type="file" accept=".js" onChange={handleFileChange} />
        </div>
        <button type="submit" style={{ marginTop: 16 }} disabled={loading}>
          {loading ? '리뷰 요청 중...' : '리뷰 요청'}
        </button>
      </form>
      {error && <div style={{ color: 'red', marginTop: 16 }}>{error}</div>}
      <hr style={{ margin: '32px 0' }} />
      <h2>리뷰 결과</h2>
      <pre style={{ background: '#f4f4f4', padding: 16, minHeight: 120 }}>{result}</pre>
    </div>
  );
}

export default App;