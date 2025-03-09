import React from 'react';
import { ScrollArea } from '../ui/scroll-area';
import { MessageCircle } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  timestamp: string;
  sender: 'user' | 'agent';
}

interface ChatHistoryProps {
  messages: Message[];
  onSelectMessage: (message: Message) => void;
}

export function ChatHistory({ messages, onSelectMessage }: ChatHistoryProps) {
  return (
    <ScrollArea className="h-[calc(100vh-4rem)] w-80 border-r">
      <div className="p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className="p-4 rounded-lg bg-white hover:bg-slate-50 cursor-pointer transition-colors"
            onClick={() => onSelectMessage(message)}
          >
            <div className="flex items-center gap-2 mb-2">
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm font-medium">
                {message.sender === 'user' ? 'User' : 'Agent'}
              </span>
            </div>
            <p className="text-sm text-slate-600 line-clamp-2">{message.content}</p>
            <span className="text-xs text-slate-400 mt-2 block">
              {new Date(message.timestamp).toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
