'use client';

import { ViewTransition } from 'react';
import FlipCard from './FlipCard';

interface Suggestion {
  restaurant_id: string;
  restaurant_name: string;
  dish_name: string;
  price: number;
  distance_km: number;
  eta_minutes: number;
  reason: string;
}

interface TrioPlateCarouselProps {
  suggestions: Suggestion[];
  clarifyQuestion?: string;
}

export default function TrioPlateCarousel({ suggestions, clarifyQuestion }: TrioPlateCarouselProps) {
  if (clarifyQuestion && suggestions.length === 0) {
    return (
      <ViewTransition enter="slide-up" exit="fade-out" default="none">
        <div className="w-full max-w-2xl mx-auto mt-8 bg-orange-50 border border-orange-200 text-orange-800 p-6 rounded-2xl text-center shadow-sm">
          <p className="text-lg font-medium">{clarifyQuestion}</p>
        </div>
      </ViewTransition>
    );
  }

  if (suggestions.length === 0) {
    return null;
  }

  return (
    <ViewTransition enter="slide-up" exit="fade-out" default="none">
      <div className="w-full mt-12 mb-8">
        <h2 className="text-xl font-bold text-gray-800 text-center mb-8">
          Đây là 3 lựa chọn tốt nhất dành cho bạn 👇
        </h2>
        
        <div className="flex flex-wrap justify-center gap-6 items-center">
          {suggestions.map((item, index) => (
            <ViewTransition key={`${item.restaurant_id}-${index}`}>
              <FlipCard item={item} index={index} />
            </ViewTransition>
          ))}
        </div>
      </div>
    </ViewTransition>
  );
}
