import { useState } from "react";
import { AutocompleteConfig } from "../../types/autocomplete";
import AutocompleteList from "../autocomplete/AutocompleteList";

interface ChatInputProps {
    placeholder?: string;
    onSend: (message: string) => void;
    autocompleteConfigs: AutocompleteConfig[];
}

const ChatInput = ({
    placeholder = "Escreva sua mensagem...",
    onSend,
    autocompleteConfigs,
}: ChatInputProps) => {
    const [message, setMessage] = useState("");
    const [activeConfig, setActiveConfig] = useState<AutocompleteConfig | null>(null);
    const [query, setQuery] = useState("");
    const [selectedIndex, setSelectedIndex] = useState(0);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setMessage(value);

        // Check for any trigger in the message
        if (activeConfig) {
            const lastTriggerIndex = activeConfig.trigger
                ? value.lastIndexOf(activeConfig.trigger)
                : -1;

            if (lastTriggerIndex === -1) {
                setActiveConfig(null);
            } else {
                const newQuery = value.slice(lastTriggerIndex + 1);
                setQuery(newQuery);
            }
        }
    };

    const handleSend = () => {
        if (message.trim()) {
            onSend(message);
            setMessage("");
            setActiveConfig(null);
        }
    };

    const handleSelect = (item: string) => {
        if (activeConfig) {
            const newMessage = activeConfig.onInsert(item, message);
            setMessage(newMessage);
            setActiveConfig(null);
            setQuery("");
            setSelectedIndex(0);
        }
    };

    const openList = (config: AutocompleteConfig) => {
        setActiveConfig(config);
        setQuery("");
        setSelectedIndex(0);
    };
    return (
        <div>
            {autocompleteConfigs.map((config, idx) => (
                config.buttonLabel && (
                    <button key={idx} onClick={() => openList(config)}>
                        {config.buttonLabel}
                    </button>
                )
            ))}

            <input
                type="text"
                value={message}
                onChange={handleChange}
                placeholder={placeholder}
                onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === "Tab") {
                        if (activeConfig) {
                            e.preventDefault();
                            const filteredItems = activeConfig.items.filter((item: string) =>
                                item.toLowerCase().includes(query.toLowerCase())
                            );
                            if (filteredItems[selectedIndex]) {
                                handleSelect(filteredItems[selectedIndex]);
                            }
                        } else if (e.key === "Enter") {
                            handleSend();
                        }
                    } else if (e.key === " " && activeConfig) {
                        setActiveConfig(null);
                    } else if (e.key === "Escape" && activeConfig) {
                        setActiveConfig(null);
                        setSelectedIndex(0);
                    } else if (e.key === "ArrowDown" && activeConfig) {
                        e.preventDefault();
                        const filteredItems = activeConfig.items.filter((item: string) =>
                            item.toLowerCase().includes(query.toLowerCase())
                        );
                        setSelectedIndex(prev => Math.min(filteredItems.length - 1, prev + 1));
                    } else if (e.key === "ArrowUp" && activeConfig) {
                        e.preventDefault();
                        setSelectedIndex(prev => Math.max(0, prev - 1));
                    } else {
                        // Check if key matches any trigger
                        const matchedConfig = autocompleteConfigs.find(
                            config => config.trigger === e.key
                        );
                        if (matchedConfig) {
                            setActiveConfig(matchedConfig);
                            setSelectedIndex(0);
                        }
                    }
                }}
            />

            {activeConfig && (
                <AutocompleteList
                    query={query}
                    items={activeConfig.items}
                    onSelect={handleSelect}
                    selectedIndex={selectedIndex}
                />
            )}

            <button onClick={handleSend}>Send</button>
        </div>
    );
};

export default ChatInput; 