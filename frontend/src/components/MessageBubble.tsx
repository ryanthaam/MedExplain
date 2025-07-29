import { Message } from '../types';
import { AlertTriangle, ExternalLink, Clock } from 'lucide-react';
import TextType from './TextType';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const bubbleClass = isUser 
    ? "bg-slate-800 text-white ml-8" 
    : "bg-teal-600 text-black mr-8";

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`my-4 p-4 rounded-xl max-w-4xl ${bubbleClass}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs opacity-70 flex items-center">
          <Clock className="w-3 h-3 mr-1" />
          {formatTimestamp(message.timestamp)}
        </span>
        {!isUser && message.confidence && (
          <span className={`text-xs px-2 py-1 rounded-full ${
            message.confidence === 'High' ? 'bg-green-500 text-white' :
            message.confidence === 'Medium' ? 'bg-yellow-500 text-black' :
            'bg-red-500 text-white'
          }`}>
            {message.confidence} Confidence
          </span>
        )}
      </div>
      
      {isUser ? (
        <div className="whitespace-pre-wrap">{message.content}</div>
      ) : (
        <TextType 
          text={message.content}
          as="div"
          className="whitespace-pre-wrap"
          typingSpeed={30}
          loop={false}
          showCursor={false}
        />
      )}
      
      {!isUser && message.safety_warning && (
        <div className="mt-3 p-3 bg-yellow-500/20 border border-yellow-500/30 rounded-lg">
          <div className="flex items-center text-yellow-300">
            <AlertTriangle className="w-4 h-4 mr-2" />
            <span className="text-sm font-semibold">Safety Warning</span>
          </div>
        </div>
      )}
      
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="mt-3 p-3 bg-slate-700/50 rounded-lg">
          <h4 className="text-sm font-semibold mb-2 text-white">Sources:</h4>
          <div className="space-y-1">
            {message.sources.map((source, index) => (
              <div key={index} className="text-xs text-slate-300 flex items-center">
                <ExternalLink className="w-3 h-3 mr-1" />
                <span>{source.drug} - {source.section}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {!isUser && message.disclaimer && (
        <div className="mt-3 p-2 bg-slate-800/50 rounded text-xs text-slate-400 border-l-2 border-teal-500">
          {message.disclaimer}
        </div>
      )}
    </div>
  );
}