import React from 'react';

interface ReviewResultProps {
  result: string;
}

const ReviewResult: React.FC<ReviewResultProps> = ({ result }) => {
  // TODO: 마크다운 렌더링 등 확장
  return <pre style={{ background: '#f4f4f4', padding: 16 }}>{result}</pre>;
};

export default ReviewResult;