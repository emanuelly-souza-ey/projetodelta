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

interface ChatContainerProps {
  autocompleteConfigs: AutocompleteConfig[];
  title: string;
}

const ChatContainer = ({ autocompleteConfigs, title }: ChatContainerProps) => {
  const [messages, setMessages] = useState<ChatBubbleProp[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showQuickReplies, setShowQuickReplies] = useState(true);
  const [showBackground, setShowBackground] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const lastMessage = messages[messages.length - 1];
  const quickReplies = lastMessage?.quickReplies;

  const handleMessage = (msg: string) => {
    setShowBackground(false);

    const timestamp = new Date().toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });

    setMessages([...messages, { message: msg, role: "user", timestamp }]);

    setIsTyping(true);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          message: `Response to: ${msg}`,
          role: "system",
          timestamp: new Date().toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
      setIsTyping(false);
    }, 1500);
  };

  const handleClear = () => {
    setMessages([]);
    setShowBackground(true);
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping]);

  useEffect(() => {
    if (lastMessage?.quickReplies) {
      setShowQuickReplies(true);
    }
  }, [lastMessage]);

  const handleQuickReply = (option: string) => {
    handleMessage(option);
    setShowQuickReplies(false);
  };

  return (
    <>
      {/* fundo com efeito de luz */}
      <LightEffect $visible={showBackground} />

      {/* container do chat */}
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

/* ------------------- STYLES ------------------- */

/* Fundo da página */
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

/* Chat sem fundo opaco — transparente */
const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 750px;
  width: 100%;
  margin: 0 auto;
  position: relative;
  padding: 0 16px;
  background-color: rgba(13, 15, 18, 0.4); /* leve transparência */
  backdrop-filter: blur(20px); /* dá um efeito de vidro fosco */
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  z-index: 1;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.4);
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 24px;
  scrollbar-width: thin;
  scrollbar-color: #444 transparent;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: #444;
    border-radius: 10px;
  }
`;

const InputArea = styled.div`
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: none;
  padding: 20px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
`;