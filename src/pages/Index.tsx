import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { VoiceInterface } from '@/components/VoiceInterface';
import { ChatInterface } from '@/components/ChatInterface';
import { ProductShowcase } from '@/components/ProductShowcase';
import heroImage from '@/assets/hero-bg.jpg';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  agentType?: 'hunter' | 'authenticator' | 'portfolio';
}

const Index = () => {
  const [activeTab, setActiveTab] = useState<'voice' | 'chat' | 'products'>('voice');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isVoiceListening, setIsVoiceListening] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);

  const handleVoiceTranscript = (text: string) => {
    console.log('Voice transcript:', text);
    // Here you would process the voice input and potentially add it as a message
    const newMessage: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "I heard you say: " + text + ". How can I help you find the perfect luxury item?",
        sender: 'agent',
        timestamp: new Date(),
        agentType: 'hunter'
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const handleChatMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text: text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    setIsChatLoading(true);

    // Simulate AI processing
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "I understand you're looking for something special. Let me search our curated collection for you.",
        sender: 'agent',
        timestamp: new Date(),
        agentType: 'hunter'
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsChatLoading(false);
    }, 1500);
  };

  const handleProductSelect = (product: any) => {
    console.log('Selected product:', product);
    // Here you would handle product selection
  };

  return (
    <div className="min-h-screen bg-gradient-dark">
      {/* Hero Section */}
      <div 
        className="relative h-screen flex items-center justify-center overflow-hidden"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed'
        }}
      >
        <div className="absolute inset-0 bg-gradient-dark opacity-70" />
        
        <div className="relative z-10 text-center max-w-4xl mx-auto px-4">
          <Badge className="mb-6 bg-primary/20 text-primary border-primary/30 text-sm">
            AI-Powered Luxury Commerce
          </Badge>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent">
            ADOGENT
          </h1>
          
          <p className="text-xl md:text-2xl text-foreground/80 mb-8 leading-relaxed">
            Your autonomous AI agents for luxury commerce.<br />
            Voice-first. Intelligent. Exclusive.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              variant="luxury" 
              size="xl"
              onClick={() => setActiveTab('voice')}
              className="transform hover:scale-105"
            >
              Start Voice Session
            </Button>
            <Button 
              variant="premium" 
              size="xl"
              onClick={() => setActiveTab('chat')}
            >
              Chat with AI Agents
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b border-primary/20">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex space-x-1 bg-card/50 p-1 rounded-lg backdrop-blur-sm">
            {[
              { id: 'voice', label: 'Voice Assistant', icon: '🎤' },
              { id: 'chat', label: 'AI Chat', icon: '💬' },
              { id: 'products', label: 'Luxury Collection', icon: '💎' }
            ].map((tab) => (
              <Button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                variant={activeTab === tab.id ? 'luxury' : 'ghost'}
                size="sm"
                className="flex-1 text-sm"
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </Button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {activeTab === 'voice' && (
          <div className="max-w-2xl mx-auto">
            <VoiceInterface
              onTranscript={handleVoiceTranscript}
              isListening={isVoiceListening}
              onToggleListening={() => setIsVoiceListening(!isVoiceListening)}
            />
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="h-[600px]">
            <ChatInterface
              onSendMessage={handleChatMessage}
              messages={messages}
              isLoading={isChatLoading}
            />
          </div>
        )}

        {activeTab === 'products' && (
          <ProductShowcase
            onProductSelect={handleProductSelect}
            title="AI-Curated Luxury Collection"
          />
        )}
      </div>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-primary/20 bg-card/30">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-muted-foreground">
            ADOGENT - Powered by AI Agents for RAISE YOUR HACK
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
