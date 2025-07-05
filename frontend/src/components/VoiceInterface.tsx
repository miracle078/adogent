import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

// Extend the Window interface to include speech recognition
declare global {
  interface Window {
    SpeechRecognition: new () => SpeechRecognition;
    webkitSpeechRecognition: new () => SpeechRecognition;
  }
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionErrorEvent) => void;
}

interface VoiceInterfaceProps {
  onTranscript?: (text: string) => void;
  isListening?: boolean;
  onToggleListening?: () => void;
}

export const VoiceInterface = ({ 
  onTranscript, 
  isListening = false, 
  onToggleListening 
}: VoiceInterfaceProps) => {
  const [transcript, setTranscript] = useState('');
  const [isRecognitionSupported, setIsRecognitionSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsRecognitionSupported(true);
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      if (recognitionRef.current) {
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
          let finalTranscript = '';
          for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            }
          }
          if (finalTranscript) {
            setTranscript(finalTranscript);
            onTranscript?.(finalTranscript);
          }
        };

        recognitionRef.current.onerror = (event: SpeechRecognitionErrorEvent) => {
          console.error('Speech recognition error:', event.error);
        };
      }
    }
  }, [onTranscript]);

  const toggleListening = () => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
    } else {
      recognitionRef.current.start();
      setTranscript('');
    }
    onToggleListening?.();
  };

  if (!isRecognitionSupported) {
    return (
      <Card className="p-6 text-center bg-gradient-card border-primary/20">
        <p className="text-muted-foreground mb-4">
          Voice recognition is not supported in your browser.
        </p>
        <p className="text-sm text-muted-foreground">
          Please use Chrome or Edge for voice features.
        </p>
      </Card>
    );
  }

  return (
    <Card className="relative overflow-hidden bg-gradient-card border-primary/20 shadow-elegant">
      <div className="absolute inset-0 bg-gradient-dark opacity-50" />
      <div className="relative p-8 text-center">
        <div className="mb-6">
          <div className={`mx-auto w-24 h-24 rounded-full border-4 transition-luxury flex items-center justify-center ${
            isListening 
              ? 'border-primary bg-primary/20 shadow-glow animate-pulse' 
              : 'border-primary/40 bg-primary/10'
          }`}>
            <div className={`w-12 h-12 rounded-full transition-luxury ${
              isListening ? 'bg-primary shadow-glow' : 'bg-primary/60'
            }`} />
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-2">Voice Assistant</h3>
          <p className="text-muted-foreground">
            {isListening ? 'Listening...' : 'Click to start voice interaction'}
          </p>
        </div>

        {transcript && (
          <div className="mb-6 p-4 bg-card border border-primary/20 rounded-lg">
            <p className="text-sm text-foreground">{transcript}</p>
          </div>
        )}

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button 
            onClick={toggleListening}
            variant={isListening ? "destructive" : "voice"}
            size="lg"
            className="min-w-32"
          >
            {isListening ? 'Stop Listening' : 'Start Voice'}
          </Button>
          
          <Badge 
            variant={isListening ? "default" : "secondary"}
            className="self-center px-3 py-1"
          >
            {isListening ? 'Active' : 'Ready'}
          </Badge>
        </div>
      </div>
    </Card>
  );
};