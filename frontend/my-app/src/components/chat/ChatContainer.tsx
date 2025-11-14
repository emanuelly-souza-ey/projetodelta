import { useEffect, useState, useRef } from "react";
import { AutocompleteConfig } from "../../types/autocomplete";
import type { ChatBubbleProp } from "./ChatBubble";
import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";
import EmptyState from "./EmptyState";
import QuickReplies from "./QuickReplies";
import TypingIndicator from "./TypingIndicator";
import styled from "styled-components";
import { sendMessageToAPI } from "../../services/api";

interface ChatContainerProps {
  autocompleteConfigs: AutocompleteConfig[];
  title: string;
}

const ChatContainer = ({ autocompleteConfigs, title }: ChatContainerProps) => {
  const [messages, setMessages] = useState<ChatBubbleProp[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [showBackground, setShowBackground] = useState(true);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const lastMessage = messages[messages.length - 1];
  const quickReplies = lastMessage?.quickReplies;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  /* --------------------------- HANDLE MESSAGE --------------------------- */

  const handleMessage = async (msg: string) => {
    setShowBackground(false);

    const timestamp = new Date().toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });

    setMessages((prev) => [
      ...prev,
      { message: msg, role: "user", timestamp },
    ]);

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
    setShowBackground(true);
    setConversationId(null);
  };

  const handleQuickReply = (option: string) => {
    handleMessage(option);
    setShowQuickReplies(false);
  };

  return (
    <>
      <LightEffect $visible={showBackground} />

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

        <InputArea>
          <ChatInput
            onSend={(msg) => {
              handleMessage(msg);
              setShowQuickReplies(false);
            }}
            autocompleteConfigs={autocompleteConfigs}
          />
        </InputArea>
      </ChatContainerWrapper>
    </>
  );
};

export default ChatContainer;

/* ------------------- STYLED COMPONENTS ------------------- */

const LightEffect = styled.div<{ $visible: boolean }>`
  position: fixed;
  inset: 0;
  background: radial-gradient(
    circle at 50% 40%,
    rgba(255, 230, 100, 0.15),
    transparent 70%
  );
  filter: blur(120px);
  pointer-events: none;
  opacity: ${({ $visible }) => ($visible ? 1 : 0)};
  transition: opacity 0.6s ease-in-out;
  z-index: 0;
`;

const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
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
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 24px;
`;

const InputArea = styled.div`
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
`;