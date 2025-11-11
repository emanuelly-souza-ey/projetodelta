interface QuickRepliesProps {
    options: string[];
    onSelect: (option: string) => void;
}

const QuickReplies = ({ options, onSelect }: QuickRepliesProps) => {
    return (
        <div className="quick-replies">
            {options.map((option, index) => (
                <button
                    key={index}
                    className="quick-reply-button"
                    onClick={() => onSelect(option)}
                >
                    {option}
                </button>
            ))}
        </div>
    );
};

export default QuickReplies;