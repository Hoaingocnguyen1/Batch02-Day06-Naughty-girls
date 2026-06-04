'use client';

import { useState } from 'react';
import ChatInputBar from './components/ChatInputBar';
import Image from 'next/image';
import TrioPlateCarousel from './components/TrioPlateCarousel';
import { ViewTransition } from 'react';

interface Suggestion {
  restaurant_id: string;
  restaurant_name: string;
  dish_name: string;
  price: number;
  distance_km: number;
  eta_minutes: number;
  reason: string;
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [clarifyQuestion, setClarifyQuestion] = useState<string>('');

  const handleSend = async (message: string) => {
    setIsLoading(true);
    setSuggestions([]);
    setClarifyQuestion('');

    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          coords: { hot: 0, cheap: 0, near: 0 },
          history: [],
          user_location: { lat: 10.762622, lng: 106.660172 }
        }),
      });

      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      
      if (data.action === 'clarify') {
        setClarifyQuestion(data.clarify_question);
      } else if (data.action === 'suggest') {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error(error);
      setClarifyQuestion('Có lỗi xảy ra, vui lòng thử lại.');
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
      <main className="flex-1 w-full max-w-4xl px-4 py-8 flex flex-col justify-center items-center">
        
        {/* Intro */}
        {suggestions.length === 0 && !clarifyQuestion && !isLoading ? (
          <ViewTransition enter="fade-in" exit="fade-out" default="none">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-extrabold text-gray-800 mb-4">
                Bạn Đang Thèm Gì?
              </h1>
              <p className="text-lg text-gray-500 max-w-md mx-auto">
                Nhập hoặc nói tên món ăn, hương vị bạn muốn. AI sẽ gợi ý cho bạn 3 lựa chọn tốt nhất!
              </p>
            </div>
          </ViewTransition>
        ) : null}

        {/* Input Bar */}
        <div className={`w-full transition-all duration-500 ${suggestions.length > 0 || clarifyQuestion || isLoading ? 'mb-8 mt-4' : 'mt-12'}`}>
          <ChatInputBar onSend={handleSend} isLoading={isLoading} />
        </div>

        {/* Loading State */}
        {isLoading ? (
          <ViewTransition enter="fade-in" exit="fade-out" default="none">
            <div className="mt-12 flex flex-col items-center justify-center space-y-4">
              <div className="text-6xl animate-bounce">🍲</div>
              <p className="text-gray-500 font-medium">Đang tìm quán ngon cho bạn…</p>
            </div>
          </ViewTransition>
        ) : null}

        {/* Results */}
        {!isLoading ? (
          <TrioPlateCarousel 
            suggestions={suggestions} 
            clarifyQuestion={clarifyQuestion} 
          />
        ) : null}
      </main>
    </div>
  );
}
