'use client';

import { useState, useRef, useEffect, startTransition } from 'react';
import { Mic, Send, MicOff, Loader2 } from 'lucide-react';

interface ChatInputBarProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInputBar({ onSend, isLoading }: ChatInputBarProps) {
  const [text, setText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize Speech Recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'vi-VN';

      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          currentTranscript += transcript;
        }
        setText(currentTranscript);
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListen = () => {
    if (!recognitionRef.current) {
      alert("Trình duyệt của bạn không hỗ trợ nhận diện giọng nói.");
      return;
    }
    
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || isLoading) return;
    
    if (isListening && recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }

    startTransition(() => {
      onSend(text);
      setText('');
    });
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="flex items-center bg-white border-2 border-gray-200 rounded-full p-2 pr-3 pl-4 shadow-sm focus-within:border-[var(--color-shopee-orange)] transition-colors w-full max-w-2xl mx-auto"
    >
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        name="message"
        aria-label="Nhập món ăn bạn muốn tìm"
        placeholder="Bạn muốn ăn gì nóng nóng, rẻ rẻ…?"
        className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400 py-2"
        disabled={isLoading}
      />
      <button
        type="button"
        onClick={toggleListen}
        className={`p-2 rounded-full transition-colors mr-2 ${isListening ? 'bg-red-100 text-red-600' : 'text-gray-400 hover:text-[var(--color-shopee-orange)] hover:bg-orange-50'}`}
        disabled={isLoading}
        title="Nhập bằng giọng nói"
        aria-label={isListening ? "Tắt nhận diện giọng nói" : "Nhập bằng giọng nói"}
      >
        {isListening ? <MicOff size={20} /> : <Mic size={20} />}
      </button>
      <button
        type="submit"
        disabled={!text.trim() || isLoading}
        className={`p-2 rounded-full text-white transition-all ${
          !text.trim() || isLoading 
            ? 'bg-gray-300 cursor-not-allowed' 
            : 'bg-[var(--color-shopee-orange)] hover:bg-orange-600 shadow-md transform hover:scale-105 active:scale-95'
        }`}
        aria-label="Gửi tin nhắn"
      >
        {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} className="ml-1" />}
      </button>
    </form>
  );
}
