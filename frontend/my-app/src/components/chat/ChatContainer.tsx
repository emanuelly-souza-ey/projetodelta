import { useEffect, useState } from "react";
import { AutocompleteConfig } from "../../types/autocomplete";
import { ChatBubbleProp } from "./ChatBubble";
import ChatHeader from "./ChatHeader";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";
import EmptyState from "./EmptyState";
import QuickReplies from "./QuickReplies";
import TypingIndicator from "./TypingIndicator";

interface ChatContainerProps {
    autocompleteConfigs: AutocompleteConfig[];
    title?: string;
}

const ChatContainer = ({
    autocompleteConfigs,
    title
}: ChatContainerProps) => {
    const [messages, setMessages] = useState<ChatBubbleProp[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [showQuickReplies, setShowQuickReplies] = useState(true);

    const lastMessage = messages[messages.length - 1];
    const quickReplies = lastMessage?.quickReplies;

    const handleMessage = (msg: string) => {
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        setMessages([...messages, { message: msg, role: "user", timestamp }]);

        setIsTyping(true);
        setTimeout(() => {
            setMessages(prev => [...prev, {
                message: `Response to: ${msg}`,
                role: "system",
                timestamp: new Date().toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                })
            }]);
            setIsTyping(false);
        }, 1500);
    };

    const handleClear = () => {
        setMessages([]);
    };

    // Reactivate quick replies when new message with options arrives
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
        <div className="chat-container">
            <ChatHeader title={title} onClear={handleClear} />

            <div className="chat-messages">
                {messages.length === 0 ? (
                    <EmptyState />
                ) : (
                    <ChatMessageList messageList={messages} />
                )}

                {isTyping && <TypingIndicator />}

                {quickReplies && showQuickReplies && (
                    <QuickReplies
                        options={quickReplies}
                        onSelect={handleQuickReply}
                    />
                )}
            </div>

            <ChatInput
                onSend={(msg) => {
                    handleMessage(msg);
                    setShowQuickReplies(false);
                }}
                autocompleteConfigs={autocompleteConfigs}
            />
        </div>
    );
};

export default ChatContainer;
