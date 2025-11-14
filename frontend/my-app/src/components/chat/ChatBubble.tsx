import { useEffect, useRef, useState } from "react";
import styled from "styled-components";

export interface ChatBubbleProp {
    message: string;
    role: string;
    timestamp?: string;
    quickReplies?: string[];
}

const ChatBubble = ({
    message = "",
    role = "",
    timestamp
}: ChatBubbleProp) => {
    const [displayedMessage, setDisplayedMessage] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const timeoutRef = useRef<number | null>(null);
    const hasTypedRef = useRef(false);

    useEffect(() => {
        if (role.toLowerCase() === "system" || role.toLowerCase() === "assistant") {
            // Si ya escribió este mensaje, no volver a escribirlo
            if (hasTypedRef.current) {
                setDisplayedMessage(message);
                return;
            }

            setIsTyping(true);
            setDisplayedMessage("");

            let currentIndex = 0;
            const totalLength = message.length;

            const typeNextChar = () => {
                if (currentIndex < totalLength) {
                    const char = message[currentIndex];
                    setDisplayedMessage(prev => prev + char);

                    // Calcular velocidad de escritura
                    let delay = 30; // velocidad base

                    // Primeras 5 letras: aceleración (más lento al inicio)
                    if (currentIndex < 5) {
                        delay = 80 - (currentIndex * 10);
                    }
                    // Últimas 5 letras: desaceleración
                    else if (currentIndex >= totalLength - 5) {
                        const remaining = totalLength - currentIndex;
                        delay = 30 + ((6 - remaining) * 15);
                    }
                    // Pausas en puntuación
                    else if (['.', ',', '!', '?', ';', ':'].includes(char)) {
                        delay = 250; // pausa larga
                    }
                    else if (char === '\n') {
                        delay = 150; // pausa media
                    }

                    currentIndex++;
                    timeoutRef.current = window.setTimeout(typeNextChar, delay);
                } else {
                    setIsTyping(false);
                    hasTypedRef.current = true;
                }
            };

            typeNextChar();

            return () => {
                if (timeoutRef.current) {
                    clearTimeout(timeoutRef.current);
                }
            };
        } else {
            setDisplayedMessage(message);
            setIsTyping(false);
        }
    }, [message, role]);

    return (
        <MessageContainer $role={role}>
            <Bubble $role={role}>
                {displayedMessage}
                {isTyping && <Cursor>|</Cursor>}
            </Bubble>
            {timestamp && <Timestamp>{timestamp}</Timestamp>}
        </MessageContainer>
    );
};

export default ChatBubble;

const MessageContainer = styled.div<{ $role: string }>`
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  align-items: ${({ $role }) =>
        $role.toLowerCase() === 'user' ? 'flex-end' : 'flex-start'};
  animation: slideIn 0.3s ease;

  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const Bubble = styled.div<{ $role: string }>`
  padding: 12px 16px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.5;
  
  ${({ $role }) => {
        const isUser = $role.toLowerCase() === 'user';

        if (isUser) {
            return `
        background: rgba(255, 230, 0, 0.35);
        color: #ffffff;
        border-bottom-right-radius: 4px;
        border: 1px solid rgba(255, 230, 0, 0.6);
      `;
        } else {
            return `
        background: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-bottom-left-radius: 4px;
      `;
        }
    }}
`;

const Timestamp = styled.span`
  font-size: 11px;
  color: #888;
  margin-top: 4px;
  margin-left: 8px;
`;

const Cursor = styled.span`
  animation: blink 0.8s infinite;
  margin-left: 2px;
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
`;