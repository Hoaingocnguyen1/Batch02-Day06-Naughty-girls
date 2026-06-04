'use client';

import { useState } from 'react';

interface Suggestion {
  restaurant_id: string;
  restaurant_name: string;
  dish_name: string;
  price: number;
  distance_km: number;
  eta_minutes: number;
  reason: string;
  image_url?: string;
  google_maps_url?: string;
}

export default function FlipCard({ item, index }: { item: Suggestion; index: number }) {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div
      className="group relative w-64 h-80 rounded-2xl cursor-pointer focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-[var(--color-shopee-orange)]"
      style={{ perspective: '1000px' }}
      onClick={() => setIsFlipped(!isFlipped)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          setIsFlipped(!isFlipped);
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`Món: ${item.dish_name} tại quán ${item.restaurant_name}`}
    >
      <div
        className={`w-full h-full transition-transform duration-500 rounded-2xl shadow-lg`}
        style={{
          transformStyle: 'preserve-3d',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
        }}
      >
        {/* Front Face */}
        <div
          className="absolute inset-0 w-full h-full bg-white rounded-2xl border border-gray-100 flex flex-col items-center justify-between p-6"
          style={{ backfaceVisibility: 'hidden' }}
        >
          {item.image_url ? (
            <div className="relative w-32 h-32 rounded-full overflow-hidden mb-4 border border-gray-100 shadow-xs">
              <img
                src={item.image_url}
                alt={item.dish_name}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          ) : (
            <div className="w-32 h-32 rounded-full bg-orange-100 flex items-center justify-center mb-4 text-4xl">
              🍲
            </div>
          )}
          <div className="text-center w-full">
            <h3 className="font-bold text-gray-800 text-lg mb-1 line-clamp-1">{item.dish_name}</h3>
            {item.google_maps_url ? (
              <a
                href={item.google_maps_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="text-sm text-gray-500 hover:text-[var(--color-shopee-orange)] hover:underline inline-flex items-center justify-center gap-1 cursor-pointer w-full font-medium"
              >
                📍 {item.restaurant_name}
              </a>
            ) : (
              <p className="text-sm text-gray-500 line-clamp-1">{item.restaurant_name}</p>
            )}
          </div>
          <div className="w-full mt-4 flex items-center justify-between text-sm font-semibold text-gray-700">
            <span className="text-[var(--color-shopee-orange)]">
              {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(item.price)}
            </span>
            <span className="bg-gray-100 px-2 py-1 rounded text-xs">
              {item.distance_km}km • {item.eta_minutes}'
            </span>
          </div>
        </div>

        {/* Back Face */}
        <div
          className="absolute inset-0 w-full h-full bg-[var(--color-shopee-orange)] rounded-2xl p-6 text-white flex flex-col items-center justify-center text-center border border-orange-500 shadow-xl"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          <div className="text-3xl mb-2">✨</div>
          <h4 className="font-bold mb-2">Vì sao chọn món này?</h4>
          <p className="text-sm leading-relaxed opacity-90 mb-4 line-clamp-4">{item.reason}</p>
          {item.google_maps_url && (
            <a
              href={item.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="px-4 py-2 bg-white text-[var(--color-shopee-orange)] font-bold text-xs rounded-full hover:bg-orange-50 transition-all duration-250 shadow-sm active:scale-95"
            >
              🗺️ Bản đồ & Chỉ đường
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
