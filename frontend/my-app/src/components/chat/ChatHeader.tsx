interface ChatHeaderProps {
    title?: string;
    onClear: () => void;
}

const ChatHeader = ({
    title = "Chat Assistant",
    onClear
}: ChatHeaderProps) => {
    return (
        <div className="chat-header">
            <h2>{title}</h2>
            <button onClick={onClear}>Clear</button>
        </div>
    );
};

export default ChatHeader;
