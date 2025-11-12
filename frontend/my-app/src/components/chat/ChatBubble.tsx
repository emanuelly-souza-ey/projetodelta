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
    return (
        <div className="chat-bubble">
            <div className="bubble-content">
                <strong>{role}:</strong> {message}
            </div>
            {timestamp && <span className="timestamp">{timestamp}</span>}
        </div>
    );
};

export default ChatBubble;