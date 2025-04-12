'use client';

import { useState } from 'react';
import Image from "next/image";

export default function Home() {
  const [videoUrl, setVideoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setTranscript([]);
    setIsLoading(true);

    try {
      // URLからビデオIDを抽出または直接ビデオIDを使用
      const videoId = videoUrl.includes('youtube.com/watch?v=')
        ? videoUrl.split('v=')[1].split('&')[0]
        : videoUrl;

      const response = await fetch('http://127.0.0.1:8000/transcript/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '文字起こしの取得に失敗しました');
      }

      const data = await response.json();
      setTranscript(data.transcript);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  // 文字起こしを表示形式に変換
  const formatTranscript = (transcriptItems) => {
    return transcriptItems.map((item, index) => {
      // 時間をフォーマット（秒から分:秒に変換）
      const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
      };

      return (
        <div key={index} className="p-3 border-b border-gray-200 hover:bg-gray-50">
          <div className="flex items-start">
            <span className="text-xs font-mono text-gray-500 w-12">
              {formatTime(item.start)}
            </span>
            <p className="flex-1 text-sm">{item.text}</p>
          </div>
        </div>
      );
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">YouTube文字起こし取得アプリ</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="videoUrl" className="block text-sm font-medium text-gray-700 mb-1">
                YouTube URL または ビデオID
              </label>
              <div className="flex">
                <input
                  type="text"
                  id="videoUrl"
                  className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                  placeholder="https://www.youtube.com/watch?v=xxxx または xxxx"
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  required
                />
                <button
                  type="submit"
                  disabled={isLoading || !videoUrl.trim()}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-r-md disabled:opacity-50"
                >
                  {isLoading ? '取得中...' : '文字起こし取得'}
                </button>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                URLまたはビデオIDを入力して、文字起こしを取得します
              </p>
            </div>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded shadow">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {transcript.length > 0 && (
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-4 bg-gray-50 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">文字起こし結果</h2>
            </div>
            <div className="divide-y divide-gray-200 max-h-[60vh] overflow-y-auto">
              {formatTranscript(transcript)}
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-center my-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        )}

        {!isLoading && !error && transcript.length === 0 && (
          <div className="bg-white shadow rounded-lg p-8 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">文字起こしを取得</h3>
            <p className="mt-1 text-sm text-gray-500">
              YouTubeのURLまたはビデオIDを入力して、文字起こしを取得してください
            </p>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-500">
            YouTube文字起こし取得アプリケーション
          </p>
        </div>
      </footer>
    </div>
  );
}