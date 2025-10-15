import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, MessageSquare, X, Minimize2, Maximize2, Send, ShoppingCart, ExternalLink, Volume2, MessageCircle } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  mode?: 'text' | 'voice';
  complete?: boolean;
  toolCall?: boolean;
  error?: boolean;
  products?: Product[];
}

interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  color: string;
  size: string;
  product_code: string;
  pricebook_entry_id: string;
  image_url?: string;
  category?: string;
}

interface VoiceAssistantProps {
  sessionId: string;
  onCartUpdate?: () => void;
  onProductClick?: (productId: string) => void;
}

const WS_BASE_URL = 'ws://localhost:8000';

export default function VoiceAssistant({ sessionId, onCartUpdate, onProductClick }: VoiceAssistantProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isAssistantSpeaking, setIsAssistantSpeaking] = useState(false);
  const [isUserSpeaking, setIsUserSpeaking] = useState(false);
  const [cartNotification, setCartNotification] = useState(false);
  const [searchResults, setSearchResults] = useState<Product[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const audioQueueRef = useRef<AudioBuffer[]>([]);
  const isPlayingRef = useRef(false);
  const currentSourceRef = useRef<AudioBufferSourceNode | null>(null);

  useEffect(() => {
    if (isOpen && !wsRef.current) {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      stopVoiceMode();
      stopAllAudio();
    };
  }, [isOpen, sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, searchResults]);

  const connectWebSocket = () => {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/chat/${sessionId}`);

    ws.onopen = () => {
      console.log('✅ Connected to voice assistant');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleServerMessage(data);
    };

    ws.onclose = () => {
      console.log('❌ Disconnected from voice assistant');
      setIsConnected(false);
      wsRef.current = null;
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const formatTime = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch {
      return '';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const handleServerMessage = (data: any) => {
    switch (data.type) {
      case 'system':
        console.log('System:', data.message);
        break;

      case 'user_speaking':
        // User started speaking - interrupt assistant immediately
        console.log('🎤 User speaking detected - stopping assistant audio');
        stopAllAudio();
        setIsAssistantSpeaking(false);
        break;

      case 'user_message':
        setMessages((prev) => [
          ...prev,
          {
            role: 'user',
            content: data.content,
            timestamp: data.timestamp,
            mode: data.mode,
          },
        ]);
        setIsUserSpeaking(false);
        // Stop assistant audio when user speaks (interruption)
        stopAllAudio();
        break;

      case 'assistant_message':
        console.log('🗣️ Assistant message:', data.content, '| Voice mode:', isVoiceMode);
        
        setMessages((prev) => {
          const filtered = prev.filter((msg) => msg.complete !== false);
          
          let lastProductMessage: Message | null = null;
          for (let i = filtered.length - 1; i >= 0; i--) {
            const msg = filtered[i];
            if (msg.role === 'system' && msg.products && msg.products.length > 0) {
              lastProductMessage = msg;
              break;
            }
          }
          
          const withoutProductMessage = lastProductMessage 
            ? filtered.filter(msg => msg !== lastProductMessage)
            : filtered;
          
          return [
            ...withoutProductMessage,
            {
              role: 'assistant',
              content: data.content,
              timestamp: data.timestamp,
              mode: data.mode,
              complete: true,
              products: lastProductMessage?.products || undefined,
            },
          ];
        });
        break;

      case 'audio_delta':
        console.log('🔊 Audio delta received | Voice mode:', isVoiceMode);
        playAudioChunk(data.audio);
        setIsAssistantSpeaking(true);
        break;

      case 'tool_call':
        console.log('🔧 Tool call:', data.tool);
        break;

      case 'tool_result':
        console.log('🔧 Tool result received:', data.tool, data.result);
        if (data.tool === 'search_products') {
          let products = [];
          if (Array.isArray(data.result)) {
            products = data.result;
          } else if (data.result?.products && Array.isArray(data.result.products)) {
            products = data.result.products;
          }
          
          console.log('📦 Search results received:', products.length, 'products');
          setSearchResults(products);
          
          setMessages((prev) => [
            ...prev,
            {
              role: 'system',
              content: '',
              timestamp: data.timestamp,
              products: products,
            },
          ]);
        } else if (data.tool === 'add_to_cart') {
          setSearchResults([]);
        }
        break;

      case 'cart_updated':
        console.log('🛒 Cart updated from voice assistant');
        if (onCartUpdate) {
          onCartUpdate();
        }
        setCartNotification(true);
        setTimeout(() => setCartNotification(false), 3000);
        break;

      case 'cart_cleared':
        console.log('🧹 Cart cleared after order');
        if (onCartUpdate) {
          onCartUpdate();
        }
        break;

      case 'error':
        setMessages((prev) => [
          ...prev,
          {
            role: 'system',
            content: `❌ ${data.message}`,
            timestamp: data.timestamp,
            error: true,
          },
        ]);
        break;
    }
  };

  const sendTextMessage = () => {
    if (!inputText.trim() || !wsRef.current) return;

    wsRef.current.send(
      JSON.stringify({
        type: 'text',
        content: inputText,
      })
    );

    setInputText('');
  };

  const toggleVoiceMode = async () => {
    if (isVoiceMode) {
      stopVoiceMode();
    } else {
      await startVoiceMode();
    }
  };

  const startVoiceMode = async () => {
    try {
      if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
          sampleRate: 24000,
        });
        console.log('🔊 Audio context created for playback');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 24000,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });
      
      streamRef.current = stream;

      const recordingContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 24000,
      });

      sourceRef.current = recordingContext.createMediaStreamSource(stream);
      processorRef.current = recordingContext.createScriptProcessor(2048, 1, 1);

      processorRef.current.onaudioprocess = (e) => {
        if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
          return;
        }

        const audioData = e.inputBuffer.getChannelData(0);
        
        // Detect if user is speaking
        let sum = 0;
        for (let i = 0; i < audioData.length; i++) {
          sum += audioData[i] * audioData[i];
        }
        const rms = Math.sqrt(sum / audioData.length);
        setIsUserSpeaking(rms > 0.01);

        const pcm16 = new Int16Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          const s = Math.max(-1, Math.min(1, audioData[i]));
          pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }

        const base64Audio = btoa(
          String.fromCharCode.apply(null, Array.from(new Uint8Array(pcm16.buffer)))
        );

        wsRef.current.send(
          JSON.stringify({
            type: 'audio',
            audio: base64Audio,
          })
        );
      };

      sourceRef.current.connect(processorRef.current);
      processorRef.current.connect(recordingContext.destination);

      setIsVoiceMode(true);
      console.log('🎤 Voice mode started');
      
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'voice_mode_on' }));
      }
      
    } catch (error) {
      console.error('Error starting voice mode:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopVoiceMode = () => {
    console.log('🛑 Stopping voice mode');

    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current.onaudioprocess = null;
      processorRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'audio_commit' }));
      wsRef.current.send(JSON.stringify({ type: 'voice_mode_off' }));
    }

    setIsVoiceMode(false);
    setIsUserSpeaking(false);
    stopAllAudio();
  };

    const stopAllAudio = () => {
    console.log('🛑 Stopping all audio playback');
    
    if (currentSourceRef.current) {
      try {
        currentSourceRef.current.stop();
        currentSourceRef.current.disconnect();
      } catch (e) {
        // Already stopped
      }
      currentSourceRef.current = null;
    }

    // Clear the queue
    const queueLength = audioQueueRef.current.length;
    audioQueueRef.current = [];
    isPlayingRef.current = false;
    setIsAssistantSpeaking(false);
    
    console.log(`🛑 Cleared ${queueLength} audio chunks from queue`);
  };

  const playAudioChunk = async (base64Audio: string) => {
    try {
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const dataView = new DataView(bytes.buffer);
      const sampleCount = bytes.length / 2;
      const float32Array = new Float32Array(sampleCount);

      for (let i = 0; i < sampleCount; i++) {
        const int16 = dataView.getInt16(i * 2, true);
        float32Array[i] = int16 / 32768;
      }

      if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
          sampleRate: 24000,
        });
        console.log('🔊 Created new audio context');
      }

      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
        console.log('▶️ Resumed audio context');
      }

      const audioBuffer = audioContextRef.current.createBuffer(1, float32Array.length, 24000);
      audioBuffer.copyToChannel(float32Array, 0);

      audioQueueRef.current.push(audioBuffer);
      
      if (!isPlayingRef.current) {
        playNextAudioBuffer();
      }
    } catch (error) {
      console.error('❌ Error playing audio:', error);
    }
  };

  const playNextAudioBuffer = () => {
    if (audioQueueRef.current.length === 0) {
      isPlayingRef.current = false;
      setIsAssistantSpeaking(false);
      console.log('⏹️ Audio playback finished');
      return;
    }

    isPlayingRef.current = true;
    const buffer = audioQueueRef.current.shift()!;

    const source = audioContextRef.current!.createBufferSource();
    source.buffer = buffer;
    source.connect(audioContextRef.current!.destination);
    
    source.onended = () => {
      currentSourceRef.current = null;
      playNextAudioBuffer();
    };
    
    currentSourceRef.current = source;
    
    try {
      source.start();
    } catch (error) {
      console.error('❌ Error starting audio source:', error);
      // Try next buffer if this one fails
      currentSourceRef.current = null;
      playNextAudioBuffer();
    }
  };

  const handleProductClick = (product: Product) => {
    if (onProductClick) {
      onProductClick(product.id);
    }
  };

  // Floating chat bubble when closed
  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end space-y-3">
        {/* Floating Chat Message */}
        <div className="bg-[#96BF48] text-white px-4 py-3 rounded-2xl rounded-br-md shadow-lg transform transition-all duration-300 opacity-100 scale-100">
          <div className="flex items-center gap-2">
            <MessageCircle size={16} />
            <span className="text-sm font-medium">Talk with AI-Assistant</span>
          </div>
        </div>

        {/* Voice Assistant Button */}
        <button
          onClick={() => setIsOpen(true)}
          className="w-16 h-16 bg-[#96BF48] text-white rounded-full shadow-lg hover:bg-[#85a840] transition-all hover:scale-110 flex items-center justify-center"
        >
          <MessageSquare size={28} />
        </button>
      </div>
    );
  }

  // Minimized state
  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end space-y-3">
        {/* Floating Chat Message (hidden when minimized) */}
        <div className="bg-[#96BF48] text-white px-4 py-3 rounded-2xl rounded-br-md shadow-lg transform transition-all duration-300 opacity-0 scale-0">
          <div className="flex items-center gap-2">
            <MessageCircle size={16} />
            <span className="text-sm font-medium">Talk with AI-Assistant</span>
          </div>
        </div>

        {/* Minimized Assistant */}
        <div className="bg-[#96BF48] text-white rounded-lg shadow-lg p-4 flex items-center gap-3">
          <MessageSquare size={24} />
          <span className="font-semibold">AI Assistant</span>
          {isConnected && (
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          )}
          {isVoiceMode && (
            <div className="flex items-center gap-1">
              <Mic size={16} className="animate-pulse" />
              <span className="text-xs">Voice Active</span>
            </div>
          )}
          <button
            onClick={() => setIsMinimized(false)}
            className="ml-2 p-1 hover:bg-[#85a840] rounded transition-colors"
          >
            <Maximize2 size={18} />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-[#85a840] rounded transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    );
  }

  // Full expanded state
  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end space-y-3">
      {/* Floating Chat Message (hidden when open) */}
      <div className="bg-[#96BF48] text-white px-4 py-3 rounded-2xl rounded-br-md shadow-lg transform transition-all duration-300 opacity-0 scale-0">
        <div className="flex items-center gap-2">
          <MessageCircle size={16} />
          <span className="text-sm font-medium">Talk with AI-Assistant</span>
        </div>
      </div>

      {/* Main Assistant Interface */}
      <div className="flex gap-4">
        {/* Voice Mode Panel - Shows when voice is active */}
        {isVoiceMode && (
          <div className="w-96 h-[600px] bg-white rounded-lg shadow-lg flex flex-col items-center justify-center relative overflow-hidden border border-gray-200">
            {/* Animated background effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-green-50/20 to-gray-50/20" />
            
            {/* Content */}
            <div className="relative z-10 flex flex-col items-center justify-center h-full">
              {/* Animated Orb */}
              <div className="relative flex items-center justify-center mb-8">
                {/* Outer glow rings */}
                {(isUserSpeaking || isAssistantSpeaking) && (
                  <>
                    <div className={`absolute w-64 h-64 rounded-full ${isUserSpeaking ? 'bg-[#96BF48]' : 'bg-[#85a840]'} opacity-20 animate-ping`} />
                    <div className={`absolute w-56 h-56 rounded-full ${isUserSpeaking ? 'bg-[#96BF48]' : 'bg-[#85a840]'} opacity-30 animate-pulse`} />
                  </>
                )}
                
                {/* Main orb */}
                <div 
                  className={`relative w-40 h-40 rounded-full transition-all duration-300 ${
                    isUserSpeaking 
                      ? 'bg-gradient-to-br from-[#96BF48] to-[#85a840] shadow-2xl shadow-[#96BF48]/50 scale-110' 
                      : isAssistantSpeaking
                      ? 'bg-gradient-to-br from-[#85a840] to-[#759639] shadow-2xl shadow-[#85a840]/50 scale-110'
                      : 'bg-gradient-to-br from-[#a8d05c] to-[#96BF48] shadow-lg'
                  }`}
                  style={{
                    animation: (isUserSpeaking || isAssistantSpeaking) ? 'pulse 1s ease-in-out infinite' : 'none',
                  }}
                >
                  {/* Inner glow */}
                  <div className="absolute inset-4 rounded-full bg-white opacity-30 blur-xl" />
                  
                  {/* Icon */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    {isUserSpeaking ? (
                      <Mic size={56} className="text-white drop-shadow-lg" />
                    ) : isAssistantSpeaking ? (
                      <Volume2 size={56} className="text-white drop-shadow-lg animate-pulse" />
                    ) : (
                      <MessageSquare size={56} className="text-white drop-shadow-lg" />
                    )}
                  </div>
                </div>
              </div>

              {/* Status Text */}
              <div className="text-center mb-6 px-4">
                <h2 className="text-2xl font-bold text-[#243746] mb-2">
                  {isUserSpeaking ? 'Listening...' : isAssistantSpeaking ? 'Speaking...' : 'Voice Mode Active'}
                </h2>
                <p className="text-gray-600">
                  {isUserSpeaking ? 'I can hear you' : isAssistantSpeaking ? 'Assistant is responding' : 'Start speaking'}
                </p>
              </div>

              {/* Close Button */}
              <button
                onClick={stopVoiceMode}
                className="absolute bottom-8 bg-red-500 hover:bg-red-600 text-white rounded-full p-4 shadow-lg transition-all hover:scale-110"
              >
                <X size={24} />
              </button>

              {/* Connection Status */}
              <div className="absolute top-4 right-4 flex items-center gap-2 bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full shadow-lg border border-gray-200">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
                <span className="text-xs font-medium text-[#243746]">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Chat Window */}
        <div className="w-96 h-[600px] bg-white rounded-lg shadow-lg flex flex-col border border-gray-200">
          {cartNotification && (
            <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 animate-bounce">
              <ShoppingCart size={18} />
              <span className="font-semibold">Item added to cart!</span>
            </div>
          )}

          <div className="bg-[#96BF48] text-white p-4 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageSquare size={24} />
              <div>
                <h3 className="font-semibold">AI Shopping Assistant</h3>
                <div className="flex items-center gap-2 text-xs">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                    }`}
                  />
                  <span>{isVoiceMode ? '🎤 Voice Mode' : '💬 Chat Mode'}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMinimized(true)}
                className="p-1 hover:bg-[#85a840] rounded transition-colors"
              >
                <Minimize2 size={18} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-[#85a840] rounded transition-colors"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <MessageSquare size={48} className="mx-auto mb-3 text-gray-400" />
                <div className="bg-white rounded-xl shadow-sm p-6 max-w-sm mx-auto border border-gray-200">
                  <p className="text-lg font-bold text-[#243746] mb-3">👋 Hi! I can help you:</p>
                  <div className="text-left space-y-2 text-sm text-gray-700 mb-4">
                    <p>• <strong>Find products</strong> - "Show me silver watches"</p>
                    <p>• <strong>Track orders</strong> - "Where's my order?"</p>
                    <p>• <strong>Browse deals</strong> - "Shoes under $100"</p>
                  </div>
                  <p className="text-xs text-gray-500 italic">Try saying: "Show me watches" or type your request</p>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx}>
                  <div
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role !== 'system' && (
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          msg.role === 'user'
                            ? 'bg-[#96BF48] text-white'
                            : 'bg-white text-[#243746] shadow-sm border border-gray-200'
                        }`}
                      >
                        {msg.content && <p className="whitespace-pre-wrap break-words">{msg.content}</p>}
                        <div
                          className={`text-xs mt-1 ${
                            msg.role === 'user' ? 'text-green-100' : 'text-gray-500'
                          }`}
                        >
                          {formatTime(msg.timestamp)}
                          {msg.mode && ` • ${msg.mode}`}
                        </div>
                      </div>
                    )}
                  </div>

                  {msg.products && msg.products.length > 0 && (
                    <div className="mt-3 grid grid-cols-2 gap-2">
                      {msg.products.map((product, pidx) => (
                        <div
                          key={pidx}
                          onClick={() => handleProductClick(product)}
                          className="bg-white rounded-lg shadow-sm overflow-hidden cursor-pointer transition-transform hover:scale-105 hover:shadow-md border border-gray-200 hover:border-[#96BF48]"
                        >
                          <div className="h-32 bg-gray-100 overflow-hidden">
                            <img
                              src={product.image_url || `https://via.placeholder.com/200x200/f8f9fa/6c757d?text=${encodeURIComponent(product.name.substring(0, 10))}`}
                              alt={product.name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                target.src = `https://via.placeholder.com/200x200/f8f9fa/6c757d?text=${encodeURIComponent(product.name.substring(0, 10))}`;
                              }}
                            />
                          </div>

                          <div className="p-2">
                            <div className="mb-1">
                              <span className="text-xs font-semibold text-[#96BF48] uppercase tracking-wide line-clamp-1">
                                {product.category || 'Product'}
                              </span>
                            </div>
                            <h4 className="text-sm font-semibold text-[#243746] line-clamp-2 mb-1">
                              {product.name}
                            </h4>
                            
                            <div className="text-xs text-gray-600 space-y-0.5 mb-2">
                              {product.color && <div>Color: {product.color}</div>}
                              {product.size && <div>Size: {product.size}</div>}
                            </div>

                            <div className="flex items-center justify-between">
                              <span className="text-lg font-bold text-[#243746]">
                                {formatCurrency(product.price)}
                              </span>
                              <ExternalLink size={14} className="text-gray-400" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                placeholder={isVoiceMode ? "Voice mode active..." : "Type a message..."}
                disabled={!isConnected || isVoiceMode}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#96BF48] focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <button
                onClick={sendTextMessage}
                disabled={!isConnected || !inputText.trim() || isVoiceMode}
                className="p-2 bg-[#96BF48] text-white rounded-lg hover:bg-[#85a840] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send size={20} />
              </button>
              <button
                onClick={toggleVoiceMode}
                disabled={!isConnected}
                className={`p-2 rounded-lg font-semibold transition-all ${
                  isVoiceMode
                    ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
                    : 'bg-[#96BF48] text-white hover:bg-[#85a840]'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                title={isVoiceMode ? "Stop voice mode" : "Start voice mode"}
              >
                {isVoiceMode ? <MicOff size={20} /> : <Mic size={20} />}
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2 text-center">
              {isVoiceMode ? '🎤 Voice active - Click mic to stop' : '💬 Click mic to start voice'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}