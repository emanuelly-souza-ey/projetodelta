import { useEffect, useRef, useState } from "react";
import styled from "styled-components";
import { sendMessageToAPI } from "../../services/api";
import { AutocompleteConfig } from "../../types/autocomplete";
import type { ChatBubbleProp } from "./ChatBubble";
import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";
import EmptyState from "./EmptyState";
import QuickReplies from "./QuickReplies";
import TypingIndicator from "./TypingIndicator";

interface ChatContainerProps {
  autocompleteConfigs: AutocompleteConfig[];
  title: string;
  onFirstMessage?: () => void;
}

const ChatContainer = ({ autocompleteConfigs, title, onFirstMessage }: ChatContainerProps) => {
  const [messages, setMessages] = useState<ChatBubbleProp[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesAreaRef = useRef<HTMLDivElement | null>(null);
  const prevMessagesLengthRef = useRef(messages.length);

  const lastMessage = messages[messages.length - 1];
  const quickReplies = lastMessage?.quickReplies;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Solo hacer scroll si se agregó un nuevo mensaje
    if (messages.length > prevMessagesLengthRef.current) {
      scrollToBottom();
      prevMessagesLengthRef.current = messages.length;
    }
  }, [messages]);

  useEffect(() => {
    // Solo hacer scroll cuando isTyping cambia a true
    if (isTyping) {
      scrollToBottom();
    }
  }, [isTyping]);

  /* --------------------------- HANDLE MESSAGE --------------------------- */

  const handleMessage = async (msg: string) => {
    const timestamp = new Date().toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });

    setMessages((prev) => {
      const newMessages = [
        ...prev,
        { message: msg, role: "user", timestamp },
      ];

      // Si es el primer mensaje, notificar al padre
      if (prev.length === 0 && onFirstMessage) {
        onFirstMessage();
      }

      return newMessages;
    });

    setIsTyping(true);

    try {
      const res = await sendMessageToAPI(msg, conversationId || undefined);

      if (!conversationId) {
        setConversationId(res.conversation_id);
      }

      const botMsg: ChatBubbleProp = {
        message: res.message,
        role: "system",
        timestamp: new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("Erro ao chamar API:", err);

      setMessages((prev) => [
        ...prev,
        {
          message: "❌ Erro ao se comunicar com o servidor.",
          role: "system",
          timestamp: new Date().toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setConversationId(null);
  };

  const handleQuickReply = (option: string) => {
    handleMessage(option);
    setShowQuickReplies(false);
  };

  return (
    <>
      <LightEffect />

      <ChatContainerWrapper>
        <ChatHeader title={title} onClear={handleClear} />

        <MessagesArea>
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              <ChatMessageList messageList={messages} />
              <div ref={messagesEndRef}></div>
            </>
          )}

          {isTyping && <TypingIndicator />}

          {quickReplies && showQuickReplies && (
            <QuickReplies options={quickReplies} onSelect={handleQuickReply} />
          )}
        </MessagesArea>
      </ChatContainerWrapper>

      <InputArea>
        <ChatInput
          onSend={(msg) => {
            handleMessage(msg);
            setShowQuickReplies(false);
          }}
          autocompleteConfigs={autocompleteConfigs}
        />
        <CreditsText>
          Desenvolvido com ❤️ por Maria Caceres e Emanuelly Souza<br />
          Apoio PMO | Thamires Azeredo e Davi Tavares
        </CreditsText>
      </InputArea>
    </>
  );
};

export default ChatContainer;

/* ------------------- STYLED COMPONENTS ------------------- */

const LightEffect = styled.div`
  position: fixed;
  inset: 0;
  background: radial-gradient(
    circle at 50% 40%,
    rgba(255, 230, 100, 0.15),
    transparent 70%
  );
  filter: blur(120px);
  pointer-events: none;
  z-index: 0;
`;

const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  max-width: 750px;
  width: 100%;
  margin: 0 auto;
  position: relative;
  padding: 0 16px;
  background-color: rgba(13, 15, 18, 0.4);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  z-index: 1;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.4);
  overflow: hidden;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 24px;
  
  /* Scrollbar personalizado */
  scrollbar-width: thin;
  scrollbar-color: #444 #1a1a1a;

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #1a1a1a;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #555;
  }
`;

const InputArea = styled.div`
  width: 100%;
  max-width: 750px;
  margin: 16px auto 0;
  padding: 0 16px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
`;

const CreditsText = styled.div`
  font-size: 0.8em;
  color: #666;
  margin-top: 12px;
  text-align: center;
  line-height: 1.5;
`;