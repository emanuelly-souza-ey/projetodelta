import ChatBubble, { ChatBubbleProp } from "./ChatBubble";

interface ChatMessageListProp {
    messageList: ChatBubbleProp[]
};

const ChatMessageList = ({
    messageList = []
}: ChatMessageListProp) => {
    return (
        <div>
            {messageList.map((msg, index) => (
                <ChatBubble
                    key={index}
                    message={msg.message}
                    role={msg.role}
                />
            ))}
        </div>
    );
};

export default ChatMessageList;