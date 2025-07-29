import { useEffect, useRef } from 'react';
import { MessageBubble } from "./MessageBubble";
import { InputBar } from "./InputBar";
import { SuggestedPrompts } from "./SuggestedPrompts";
import { CommandBar } from "./CommandBar";
import { useChat } from '../hooks/useChat';
import { AlertCircle, Trash2 } from 'lucide-react';
import TextType from "./TextType";

export function ChatWindow() {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = (message: string) => {
    sendMessage(message);
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-800 p-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-teal-400">MedExplain Chat</h1>
          <p className="text-sm text-slate-400">Ask questions about medications</p>
        </div>
        {hasMessages && (
          <button
            onClick={clearMessages}
            className="flex items-center gap-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm transition-colors"
            disabled={isLoading}
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {!hasMessages && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <TextType 
                text={[
                  "Welcome to MedExplain",
                  "Your AI Medication Assistant", 
                  "FDA-Sourced Drug Information",
                  "Ask About Any Medication"
                ]}
                as="h2"
                className="text-2xl font-bold mb-4"
                typingSpeed={100}
                pauseDuration={2000}
                deletingSpeed={50}
                loop={true}
                showCursor={true}
                cursorCharacter="|"
                cursorClassName="text-teal-400"
                textColors={["#ffffff", "#14b8a6", "#ffffff", "#14b8a6"]}
              />
              <TextType 
                text="Ask questions about medications and get FDA-sourced answers"
                as="p"
                className="text-slate-400 mb-8"
                typingSpeed={60}
                initialDelay={1500}
                loop={false}
                showCursor={false}
              />
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {error && (
          <div className="my-4 p-4 bg-red-500/20 border border-red-500/30 rounded-xl flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-3 flex-shrink-0" />
            <span className="text-red-300">{error}</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-800 bg-slate-900">
        <SuggestedPrompts onSelectPrompt={handleSendMessage} isLoading={isLoading} />
        <CommandBar onSelectCommand={handleSendMessage} isLoading={isLoading} />
        <InputBar onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
}