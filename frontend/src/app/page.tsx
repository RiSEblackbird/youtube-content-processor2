'use client';

import { useState } from 'react';

interface TranscriptItem {
  start: number;
  text: string;
}

interface ChatMessage {
  type: 'user' | 'ai';
  content: string;
}

export default function Home() {
  const [videoUrl, setVideoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState<TranscriptItem[]>([]);
  const [summary, setSummary] = useState('');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [error, setError] = useState('');
  const [isTranscriptExpanded, setIsTranscriptExpanded] = useState(true);
  const [videoTitle, setVideoTitle] = useState('');
  const [videoDescription, setVideoDescription] = useState('');
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [channelTitle, setChannelTitle] = useState('');
  const [channelUrl, setChannelUrl] = useState('');
  // チャット関連の状態
  const [chatType, setChatType] = useState('transcript');
  const [chatMessage, setChatMessage] = useState('');
  const [transcriptChatMessages, setTranscriptChatMessages] = useState<ChatMessage[]>([]);
  const [summaryChatMessages, setSummaryChatMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setTranscript([]);
    setSummary(''); // 要約をリセット
    setError('');
    setVideoTitle('');
    setVideoDescription('');
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
      setVideoTitle(data.title);
      setVideoDescription(data.description);
      setChannelTitle(data.channelTitle);
      setChannelUrl(data.channelId);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSummarize = async () => {
    setError('');
    setIsSummarizing(true);

    try {
      const videoId = videoUrl.includes('youtube.com/watch?v=')
        ? videoUrl.split('v=')[1].split('&')[0]
        : videoUrl;

      const response = await fetch('http://127.0.0.1:8000/summarize/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '要約の生成に失敗しました');
      }

      const data = await response.json();
      setSummary(data.summary);
      setIsTranscriptExpanded(false); // 要約完了時に文字起こしを折りたたむ
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setIsSummarizing(false);
    }
  };

  // チャットメッセージ送信処理
  const handleSendMessage = async () => {
    if (!chatMessage.trim() || isChatLoading) return;

    const newMessage: ChatMessage = { type: 'user' as const, content: chatMessage };
    if (chatType === 'transcript') {
      setTranscriptChatMessages(prev => [...prev, newMessage]);
    } else {
      setSummaryChatMessages(prev => [...prev, newMessage]);
    }
    setChatMessage('');
    setIsChatLoading(true);

    try {
      const contentText = chatType === 'transcript' 
        ? transcript.map(item => item.text).join(' ')
        : summary;

      const response = await fetch('http://127.0.0.1:8000/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: chatMessage,
          type: chatType,
          contentText: contentText,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'チャットの応答に失敗しました');
      }

      const data = await response.json();
      const aiMessage: ChatMessage = { type: 'ai' as const, content: data.response };
      if (chatType === 'transcript') {
        setTranscriptChatMessages(prev => [...prev, aiMessage]);
      } else {
        setSummaryChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setIsChatLoading(false);
    }
  };

  // 文字起こしを表示形式に変換
  const formatTranscript = (transcriptItems: TranscriptItem[]) => {
    return transcriptItems.map((item, index) => {
      // 時間をフォーマット（秒から分:秒に変換）
      const formatTime = (seconds: number) => {
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

      <main className="max-w-7xl mx-auto px-4 py-8 flex">
        <div className="flex-1 mr-4">
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
                    className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border text-black"
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

          {/* 動画タイトル部分 */}
          {videoTitle && (
            <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
              <div className="p-4 bg-gray-50 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">動画タイトル</h2>
              </div>
              <div className="p-4 text-black">
                <p>{videoTitle}</p>
                {channelTitle && (
                  <a
                    href={`https://www.youtube.com/channel/${channelUrl}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 mt-2 inline-block"
                  >
                    {channelTitle}
                  </a>
                )}
              </div>
              <div className="relative p-4 border-t border-gray-200">
                <button
                  onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                  className="text-blue-600 hover:text-blue-800 mb-2 flex items-center"
                >
                  <span className="mr-2">動画の説明</span>
                  <svg
                    className={`h-5 w-5 transform transition-transform ${
                      isDescriptionExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                {isDescriptionExpanded && (
                  <p className="mt-2 text-gray-600 whitespace-pre-wrap">
                    {videoDescription}
                  </p>
                )}
              </div>
            </div>
          )}

          {transcript.length > 0 && (
            <div className="space-y-4">
              {summary && (
                <div className="space-y-4">
                  <div className="bg-white shadow overflow-hidden sm:rounded-lg p-4 my-4">
                    <div className="flex justify-between items-start">
                      <h2 className="text-lg font-medium text-gray-900">要約結果</h2>
                    </div>
                    <div className="mt-4 space-y-4">
                      {(() => {
                        try {
                          const summaryData = JSON.parse(summary);
                          return (
                            <>
                              <div>
                                <h3 className="text-md font-medium">サブタイトル</h3>
                                <p className="text-gray-600">{summaryData.sub_title}</p>
                              </div>
                              <div>
                                <h3 className="text-md font-medium">概要</h3>
                                <p className="text-gray-600 whitespace-pre-wrap">{summaryData.overview}</p>
                              </div>
                              <div>
                                <h3 className="text-md font-medium">主要トピック</h3>
                                <ul className="list-disc list-inside text-gray-600">
                                  {summaryData.main_topics.map((topic, index) => (
                                    <li key={index}>{topic}</li>
                                  ))}
                                </ul>
                              </div>
                              <div>
                                <h3 className="text-md font-medium">重要ポイント</h3>
                                <div className="space-y-2">
                                  {summaryData.key_points.map((point, index) => (
                                    <div key={index}>
                                      <p className="font-medium text-gray-700">{point.title}</p>
                                      <p className="text-gray-600">{point.description}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <h3 className="text-md font-medium">キーワード</h3>
                                <p className="text-gray-600">{summaryData.keywords.join(', ')}</p>
                              </div>
                              <div>
                                <h3 className="text-md font-medium">アクションアイテム</h3>
                                <ul className="list-disc list-inside text-gray-600">
                                  {summaryData.action_items.map((item, index) => (
                                    <li key={index}>{item}</li>
                                  ))}
                                </ul>
                              </div>
                            </>
                          );
                        } catch {
                          return <p className="text-red-500">要約データの解析に失敗しました。</p>;
                        }
                      })()}
                    </div>
                  </div>

                  {/* JSON生データ表示セクション */}
                  <div className="bg-white shadow overflow-hidden sm:rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <h2 className="text-lg font-medium text-gray-900">要約生データ（JSON）</h2>
                    </div>
                    <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm font-mono text-gray-700">
                      {JSON.stringify(JSON.parse(summary), null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              {/* 文字起こし部分 */}
              <div className="bg-white shadow rounded-lg overflow-hidden">
                <div className="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setIsTranscriptExpanded(!isTranscriptExpanded)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <svg
                        className={`h-5 w-5 transform transition-transform ${
                          isTranscriptExpanded ? 'rotate-0' : '-rotate-90'
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </button>
                    <h2 className="text-lg font-medium text-gray-900">文字起こし結果</h2>
                  </div>
                  <button
                    onClick={handleSummarize}
                    disabled={isSummarizing}
                    className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                  >
                    {isSummarizing ? '要約中...' : '文字起こし要約'}
                  </button>
                </div>
                {isTranscriptExpanded && (
                  <div className="divide-y divide-gray-200 max-h-[60vh] overflow-y-auto">
                    {formatTranscript(transcript)}
                  </div>
                )}
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
        </div>

        {/* チャットサイドバー */}
        <div className="w-96 bg-white shadow rounded-lg overflow-hidden flex flex-col h-[calc(100vh-12rem)]">
          <div className="p-4 bg-gray-50 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">チャット</h2>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setChatType('transcript')}
                  className={`px-3 py-1 rounded-md text-sm ${
                    chatType === 'transcript'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  文字起こし
                </button>
                <button
                  onClick={() => setChatType('summary')}
                  className={`px-3 py-1 rounded-md text-sm ${
                    chatType === 'summary'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  要約
                </button>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {(chatType === 'transcript' ? transcriptChatMessages : summaryChatMessages).map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 relative ${
                    msg.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  {msg.content}
                  {msg.type === 'user' && (
                    <span className="absolute -top-2 right-2 text-xs text-gray-500 bg-white px-1 rounded">
                      {chatType === 'transcript' ? '文字起こし' : '要約'}
                    </span>
                  )}
                </div>
              </div>
            ))}
            {isChatLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                disabled={isChatLoading || !(transcript.length > 0 || summary)}
                placeholder={
                  transcript.length > 0 || summary
                    ? "メッセージを入力..."
                    : "文字起こしまたは要約を取得してください"
                }
                className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 text-black"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage();
                  }
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={isChatLoading || !chatMessage.trim() || !(transcript.length > 0 || summary)}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md disabled:opacity-50"
              >
                送信
              </button>
            </div>
          </div>
        </div>
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