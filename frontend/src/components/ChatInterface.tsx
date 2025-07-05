import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentType?: 'hunter' | 'authenticator' | 'portfolio';
}

interface ChatInterfaceProps {
  onSendMessage?: (message: string) => void;
  messages?: Message[];
  isLoading?: boolean;
}

export const ChatInterface = ({ 
  onSendMessage, 
  messages = [], 
  isLoading = false 
}: ChatInterfaceProps) => {
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputMessage.trim()) {
      onSendMessage?.(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getAgentBadgeColor = (agentType?: string) => {
    switch (agentType) {
      case 'hunter': return 'bg-primary/20 text-primary border-primary/30';
      case 'authenticator': return 'bg-accent/20 text-accent border-accent/30';
      case 'portfolio': return 'bg-secondary/20 text-secondary-foreground border-secondary/30';
      default: return 'bg-muted/20 text-muted-foreground border-muted/30';
    }
  };

  return (
    <Card className="flex flex-col h-full bg-gradient-card border-primary/20 shadow-elegant">
      {/* Header */}
      <div className="p-4 border-b border-primary/20 bg-gradient-dark">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">ADOGENT Chat</h3>
          <Badge className="bg-primary/20 text-primary border-primary/30">
            AI Agents Active
          </Badge>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary/20 rounded-full flex items-center justify-center">
                <div className="w-8 h-8 bg-primary/60 rounded-full" />
              </div>
              <p className="text-muted-foreground mb-2">Welcome to ADOGENT</p>
              <p className="text-sm text-muted-foreground">
                Start a conversation with our AI agents
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 transition-luxury ${
                    message.sender === 'user'
                      ? 'bg-primary text-primary-foreground shadow-glow'
                      : 'bg-card border border-primary/20 shadow-elegant'
                  }`}
                >
                  {message.sender === 'agent' && message.agentType && (
                    <Badge 
                      className={`mb-2 text-xs ${getAgentBadgeColor(message.agentType)}`}
                    >
                      {message.agentType.charAt(0).toUpperCase() + message.agentType.slice(1)} Agent
                    </Badge>
                  )}
                  <p className="text-sm leading-relaxed">{message.text}</p>
                  <p className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-card border border-primary/20 rounded-lg p-3 shadow-elegant">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-primary/20 bg-gradient-dark">
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask our AI agents anything..."
            className="flex-1 bg-card border-primary/20 focus:border-primary/40 focus:ring-primary/20"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isLoading}
            variant="luxury"
            size="default"
          >
            Send
          </Button>
        </div>
      </div>
    </Card>
  );
};