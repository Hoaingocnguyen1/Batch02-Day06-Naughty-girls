'use client';

import { useState, useRef, useEffect } from 'react';
import ChatInputBar from './components/ChatInputBar';
import Image from 'next/image';
import TrioPlateCarousel from './components/TrioPlateCarousel';

interface Suggestion {
  restaurant_id: string;
  restaurant_name: string;
  dish_name: string;
  price: number;
  distance_km: number;
  eta_minutes: number;
  reason: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  suggestions?: Suggestion[];
  action?: 'suggest' | 'clarify' | 'fallback';
  fallback_url?: string;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (message: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      // Build chat history matching backend expectations (excluding current message)
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        message: msg.content
      }));

      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          history: chatHistory,
          user_location: { lat: 10.776, lng: 106.701 } // mặc định Quận 1, HCM
        }),
      });

      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      
      let assistantMsg: Message;

      if (data.action === 'clarify') {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.clarify_question,
          action: 'clarify'
        };
      } else if (data.action === 'suggest') {
        const mappedSuggestions = (data.suggestions || []).map((s: any) => ({
          restaurant_id: s.restaurant_id || '',
          restaurant_name: s.restaurant_name || '',
          dish_name: s.dish_name || '',
          price: s.price || 0,
          distance_km: s.distance_km || 0,
          eta_minutes: s.eta_mins || s.eta_minutes || 0,
          reason: s.reason || ''
        }));

        assistantMsg = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Dưới đây là 3 lựa chọn phù hợp nhất mà mình tìm được cho bạn. Bấm vào thẻ để xem lý do gợi ý nha! 👇',
          suggestions: mappedSuggestions,
          action: 'suggest'
        };
      } else if (data.action === 'fallback') {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.message || 'Mình chỉ có thể gợi ý chọn món ăn trên ShopeeFood thôi nha.',
          action: 'fallback',
          fallback_url: data.fallback_url
        };
      } else {
        assistantMsg = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Hệ thống phản hồi không xác định. Bạn muốn ăn món gì khác không?'
        };
      }

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Ối, đã có lỗi kết nối đến máy chủ. Bạn vui lòng thử lại sau nha!',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 items-center font-sans">
      {/* Header */}
      <header className="w-full bg-white shadow-sm p-4 sticky top-0 z-10 flex justify-center border-b border-gray-100">
        <Image
          src="/shopee-food-indonesia-seeklogo.png"
          alt="Shopee Food Logo"
          width={180}
          height={60}
          priority
          className="object-contain"
        />
      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-4xl px-4 py-8 flex flex-col justify-between">
        
        {/* Intro */}
        {messages.length === 0 && !isLoading ? (
          <div className="text-center my-auto flex flex-col items-center animate-fade-in">
            <h1 className="text-4xl font-extrabold text-gray-800 mb-4 tracking-tight">
              Bạn Đang Thèm Gì?
            </h1>
            <p className="text-lg text-gray-500 max-w-md mx-auto mb-8 leading-relaxed">
              Nhập hoặc nói tên món ăn, hương vị bạn muốn. Trợ lý AI sẽ gợi ý cho bạn 3 lựa chọn tốt nhất!
            </p>
            
            {/* Quick Suggestion Chips */}
            <div className="flex flex-wrap justify-center gap-3 max-w-xl px-4">
              {[
                'Cơm gà xối mỡ ngon rẻ', 
                'Trà sữa ít ngọt gần đây', 
                'Món cháo nóng cho người ốm', 
                'Bún đậu mắm tôm chuẩn vị'
              ].map((suggestionText) => (
                <button
                  key={suggestionText}
                  id={`suggestion-${suggestionText.replace(/\s+/g, '-').toLowerCase()}`}
                  onClick={() => handleSend(suggestionText)}
                  className="px-4 py-2.5 bg-white hover:bg-orange-50 border border-gray-200 hover:border-[var(--color-shopee-orange)] rounded-full text-sm text-gray-600 hover:text-[var(--color-shopee-orange)] shadow-xs transition-all duration-200 cursor-pointer active:scale-95 font-medium"
                >
                  💡 {suggestionText}
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {/* Chat History Area */}
        {messages.length > 0 ? (
          <div className="flex-1 w-full max-w-3xl mx-auto flex flex-col space-y-6 overflow-y-auto mb-6 pr-2 max-h-[65vh] scrollbar-thin">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${
                  msg.role === 'user' ? 'items-end' : 'items-start'
                }`}
              >
                {/* Chat message wrapper */}
                <div className={`flex items-start space-x-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-red-500 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0">
                      AI
                    </div>
                  )}
                  
                  <div className="flex flex-col">
                    <div
                      className={`px-4 py-3 rounded-2xl shadow-xs text-sm leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-[var(--color-shopee-orange)] text-white rounded-tr-none'
                          : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      
                      {/* Actions/Fallback links */}
                      {msg.action === 'fallback' && msg.fallback_url && (
                        <div className="mt-3">
                          <a
                            href={msg.fallback_url}
                            id={`fallback-btn-${msg.id}`}
                            className="inline-block px-4 py-2 bg-[var(--color-shopee-orange)] hover:bg-orange-600 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
                          >
                            Duyệt tất cả quán ăn ➜
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Suggestions Carousel rendered inline below the message */}
                {msg.role === 'assistant' && msg.action === 'suggest' && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="w-full mt-4 pl-11">
                    <TrioPlateCarousel
                      suggestions={msg.suggestions}
                    />
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading status inside chat */}
            {isLoading && (
              <div className="flex items-start space-x-3 self-start max-w-[85%]">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-red-500 text-white flex items-center justify-center font-bold text-xs shadow-sm flex-shrink-0 animate-pulse">
                  AI
                </div>
                <div className="bg-white border border-gray-100 text-gray-500 px-4 py-3 rounded-2xl rounded-tl-none shadow-xs text-sm flex items-center space-x-2">
                  <div className="flex space-x-1.5">
                    <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span>Đang chọn quán ngon...</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        ) : null}

        {/* Initial loading screen */}
        {isLoading && messages.length === 0 ? (
          <div className="my-auto flex flex-col items-center justify-center space-y-4 animate-fade-in">
            <div className="text-6xl animate-bounce">🍲</div>
            <p className="text-gray-500 font-medium">Đang tìm quán ngon cho bạn…</p>
          </div>
        ) : null}

        {/* Input Bar & Clean Chat Button */}
        <div className="w-full mt-auto flex flex-col items-center space-y-4">
          <ChatInputBar onSend={handleSend} isLoading={isLoading} />
          
          {messages.length > 0 && (
            <button
              onClick={() => setMessages([])}
              id="btn-clear-chat"
              className="text-xs text-gray-400 hover:text-[var(--color-shopee-orange)] transition-colors underline cursor-pointer"
            >
              Xóa lịch sử hội thoại
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
