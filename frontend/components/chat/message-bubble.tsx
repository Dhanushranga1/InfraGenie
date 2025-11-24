/**
 * Message Bubble Component
 * 
 * Individual chat message with role-based styling and markdown support
 */

import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  role: 'user' | 'ai';
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === 'user';
  
  return (
    <div
      className={cn(
        'flex gap-3 mb-4',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Icon */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-violet-600'
            : 'bg-zinc-800 border border-zinc-700'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-violet-400" />
        )}
      </div>
      
      {/* Message Bubble */}
      <div
        className={cn(
          'px-4 py-3 rounded-2xl max-w-[85%] break-words',
          isUser
            ? 'bg-violet-600 text-white rounded-tr-none'
            : 'bg-zinc-800 text-zinc-100 rounded-tl-none'
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold text-violet-300">{children}</strong>,
                code: ({ children, className }) => {
                  const isInline = !className;
                  return isInline ? (
                    <code className="bg-zinc-900 text-emerald-400 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
                  ) : (
                    <code className="block bg-zinc-900 text-emerald-400 px-3 py-2 rounded text-xs font-mono overflow-x-auto">{children}</code>
                  );
                },
                ul: ({ children }) => <ul className="list-disc list-inside space-y-1 my-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2">{children}</ol>,
                li: ({ children }) => <li className="text-zinc-300">{children}</li>,
                h3: ({ children }) => <h3 className="text-base font-semibold text-zinc-200 mt-3 mb-1">{children}</h3>,
                blockquote: ({ children }) => <blockquote className="border-l-2 border-violet-500 pl-3 italic text-zinc-400">{children}</blockquote>,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
