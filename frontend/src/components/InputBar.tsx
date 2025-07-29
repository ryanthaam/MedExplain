import { useState, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface InputBarProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export function InputBar({ onSendMessage, isLoading }: InputBarProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center bg-slate-800 p-3 rounded-xl mt-2">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        className="flex-1 bg-transparent outline-none text-white placeholder-slate-400 px-3"
        placeholder="Ask about medications... (e.g., 'What are the side effects of Ibuprofen?')"
        disabled={isLoading}
      />
      <button 
        onClick={handleSend}
        disabled={!input.trim() || isLoading}
        className="ml-2 bg-teal-500 hover:bg-teal-400 disabled:bg-slate-600 disabled:cursor-not-allowed text-black px-4 py-2 rounded-xl transition-colors flex items-center"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
      </button>
    </div>
  );
}