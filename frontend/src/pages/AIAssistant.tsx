import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { ArrowLeft, Send, Mic, MicOff, Bot, User, Volume2, VolumeX, Upload, X, Image } from 'lucide-react';
import { toast } from "sonner";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  image?: string;
}

interface FavoriteItem {
  title: string;
}

const plantList = [
  'tomato', 'wheat', 'corn', 'rice', 'potato', 'carrot',
  'lettuce', 'apple', 'orange', 'strawberry', 'cotton', 'soybean'
];

const getPlantInterests = (favorites: FavoriteItem[]) => {
  const interests: Record<string, string[]> = {};
  for (const item of favorites) {
    const title = item.title.toLowerCase();
    for (const plant of plantList) {
      if (title.includes(plant)) {
        if (!interests[plant]) interests[plant] = [];
        interests[plant].push(item.title);
      }
    }
  }
  return interests;
};

const AIAssistant = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your AI assistant for luxury goods. How can I assist you today?",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_BACKEND_URL}/api/user/favorites`)
      .then(res => res.json())
      .then(data => setFavorites(data.favorites || []));
  }, []);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error("Image size should be less than 5MB");
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setUploadedImage(result);
        toast.success("Image uploaded successfully!");
      };
      reader.readAsDataURL(file);
    }
  };

  const removeUploadedImage = () => {
    setUploadedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const analyzePlantImage = async (base64Image: string): Promise<string> => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64Image }),
      });

      const result = await response.json();
      if (!result.result) return "No prediction result.";
      return typeof result.result === "string" ? result.result : JSON.stringify(result.result);
    } catch (error) {
      console.error("Backend error:", error);
      return "Image analysis failed.";
    }
  };

  const handleSendMessage = async () => {
    if ((!inputValue.trim() && !uploadedImage) || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue || "Please analyze this image",
      isUser: true,
      timestamp: new Date(),
      image: uploadedImage || undefined,
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setUploadedImage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    setIsLoading(true);

    if (uploadedImage) {
      try {
        const analysisResult = await analyzePlantImage(userMessage.image!);
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: analysisResult,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } catch (error) {
        console.error("Image analysis error:", error);
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(),
          content: "Image analysis failed.",
          isUser: false,
          timestamp: new Date(),
        }]);
      } finally {
        setIsLoading(false);
      }
      return;
    }

    const chatHistory = [
      ...messages,
      userMessage
    ].map(msg => ({
      role: msg.isUser ? 'user' : 'assistant',
      content: msg.content
    }));

    const interests = getPlantInterests(favorites);
    const interestsPrompt = Object.entries(interests).map(([plant, items]) =>
      `The user is interested in ${plant}. Saved items:\n${items.map(t => `- ${t}`).join('\n')}`
    ).join('\n\n');

    chatHistory.unshift({
      role: "system",
      content: `You are an AI assistant for a luxury commerce platform. Based on the user's favorites, assist in luxury shopping decisions.\n\n${interestsPrompt}`
    });

    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: chatHistory }),
      });

      const data = await response.json();

      const aiResponse: Message = {
        id: (Date.now() + 2).toString(),
        content: data.reply || "Sorry, I couldn't get a response from the AI at this time.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error("API error:", error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 2).toString(),
        content: "An error occurred while communicating with the AI.",
        isUser: false,
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      toast.error("Speech recognition is not supported in this browser");
      return;
    }

    const SpeechRecognitionConstructor = window.webkitSpeechRecognition;
    const recognition = new SpeechRecognitionConstructor();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();
    setIsListening(true);
    toast.info("Listening...");

    recognition.onresult = (event: Event) => {
      const results = (event as SpeechRecognitionEvent).results;
      const transcript = results[0][0].transcript;
      setInputValue(transcript);
      toast.success("Voice input captured!");
      setIsListening(false);
    };

    recognition.onerror = () => {
      toast.error("Speech recognition error");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };
  };

  const handleTextToSpeech = (text: string) => {
    if ('speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      } else {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
      }
    } else {
      toast.error("Text-to-speech not supported in this browser");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-800">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 text-white hover:text-blue-300 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Home</span>
          </Link>
          <Badge variant="secondary" className="bg-blue-500/20 text-blue-300">
            AI Assistant
          </Badge>
        </div>
      </header>

      {/* Chat Interface */}
      <div className="container mx-auto px-4 pb-6">
        <div className="max-w-4xl mx-auto">
          {/* Chat Header */}
          <Card className="bg-white/10 backdrop-blur-lg border-white/20 mb-6">
            <CardContent className="p-6 text-center">
              <Bot className="w-12 h-12 text-blue-400 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-white mb-2">AI Assistant</h1>
              <p className="text-gray-300">
                I can help with luxury shopping, price comparison, product authentication, and portfolio management.
              </p>
            </CardContent>
          </Card>

          {/* Chat Messages */}
          <Card className="bg-white/10 backdrop-blur-lg border-white/20 mb-6">
            <CardContent className="p-0">
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl p-4 ${
                        message.isUser
                          ? 'bg-blue-500 text-white'
                          : 'bg-white/20 text-white border border-white/10'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {!message.isUser && (
                          <Bot className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                        )}
                        {message.isUser && (
                          <User className="w-5 h-5 text-white mt-0.5 flex-shrink-0" />
                        )}
                        <div className="flex-1">
                          {message.image && (
                            <div className="mb-3">
                              <img 
                                src={message.image} 
                                alt="Uploaded" 
                                className="max-w-full h-auto rounded-lg max-h-48 object-cover"
                              />
                            </div>
                          )}
                          <p className="text-sm leading-relaxed">{message.content}</p>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs opacity-70">
                              {message.timestamp.toLocaleTimeString()}
                            </span>
                            {!message.isUser && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleTextToSpeech(message.content)}
                                className="h-6 w-6 p-0 text-white/70 hover:text-white"
                              >
                                {isSpeaking ? (
                                  <VolumeX className="w-3 h-3" />
                                ) : (
                                  <Volume2 className="w-3 h-3" />
                                )}
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white/20 rounded-2xl p-4 border border-white/10">
                      <div className="flex items-center space-x-2">
                        <Bot className="w-5 h-5 text-blue-400" />
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </CardContent>
          </Card>

          {/* Input Area */}
          <Card className="bg-white/10 backdrop-blur-lg border-white/20">
            <CardContent className="p-4">
              {uploadedImage && (
                <div className="mb-4 relative inline-block">
                  <img 
                    src={uploadedImage} 
                    alt="Preview" 
                    className="max-w-xs h-auto rounded-lg max-h-32 object-cover"
                  />
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={removeUploadedImage}
                    className="absolute -top-2 -right-2 h-6 w-6 p-0 rounded-full"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              )}
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleVoiceInput}
                  className={`border-white/20 ${isListening ? 'bg-red-500 text-white' : 'text-white hover:bg-white/10'}`}
                >
                  {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  className="border-white/20 text-white hover:bg-white/10"
                >
                  <Upload className="w-4 h-4" />
                </Button>

                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask about luxury goods or upload a product image"
                  className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
                  disabled={isLoading}
                />
                
                <Button
                  onClick={handleSendMessage}
                  disabled={(!inputValue.trim() && !uploadedImage) || isLoading}
                  className="bg-blue-500 hover:bg-blue-600 text-white"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;


