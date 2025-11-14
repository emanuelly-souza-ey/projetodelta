import { useState } from "react";
import { IoAt, IoSend } from "react-icons/io5";
import styled from "styled-components";
import type { AutocompleteConfig } from "../../types/autocomplete";
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
    <InputWrapper>
      <ButtonsContainer>
        {autocompleteConfigs.map(
          (config, idx) =>
            config.buttonLabel && (
              <TriggerButton key={idx} onClick={() => openList(config)}>
                {config.buttonLabel}
              </TriggerButton>
            )
        )}
      </ButtonsContainer>

      <InputContainer>
        {activeConfig && (
          <AutocompleteList
            query={query}
            items={activeConfig.items}
            onSelect={handleSelect}
            selectedIndex={selectedIndex}
          />
        )}

        <StyledInput
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
              setSelectedIndex((prev) => Math.min(filteredItems.length - 1, prev + 1));
            } else if (e.key === "ArrowUp" && activeConfig) {
              e.preventDefault();
              setSelectedIndex((prev) => Math.max(0, prev - 1));
            } else {
              const matchedConfig = autocompleteConfigs.find(
                (config) => config.trigger === e.key
              );
              if (matchedConfig) {
                setActiveConfig(matchedConfig);
                setSelectedIndex(0);
              }
            }
          }}
        />

        <ActionButton
          onClick={() => {
            const mentionConfig = autocompleteConfigs.find(c => c.trigger === "@");
            if (mentionConfig) {
              openList(mentionConfig);
            }
          }}
          title="Mencionar pessoa"
        >
          <IoAt />
        </ActionButton>

        <SendButton
          onClick={handleSend}
          disabled={!message.trim()}
          $active={!!message.trim()}
        >
          <IoSend />
        </SendButton>
      </InputContainer>
    </InputWrapper>
  );
};

export default ChatInput;


const InputWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
`;

const InputContainer = styled.div`
  position: relative;
  display: flex;
  align-items: center;
  background-color: #1a1b1e;
  border: 2px solid transparent;
  background-image: 
    linear-gradient(#1a1b1e, #1a1b1e),
    linear-gradient(90deg, #656579 0%, #c6b200 50%, #656579 100%);
  background-origin: border-box;
  background-clip: padding-box, border-box;
  border-radius: 14px;
  padding: 10px 14px;
  width: 100%;
  /* max-width: 750px;
  /* margin: 0 auto;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.25);

  &:focus-within {
    background-image: 
      linear-gradient(#1a1b1e, #1a1b1e),
      linear-gradient(90deg, #656579 0%, #d4c000 50%, #656579 100%);
  }
`;

const StyledInput = styled.input`
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  font-size: 15px;
  padding-right: 10px;

  &::placeholder {
    color: #aaa;
  }
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #888;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, color 0.2s ease;
  margin-right: 8px;

  &:hover {
    transform: scale(1.1);
    color: #aaa;
  }
`;

const SendButton = styled.button<{ $active: boolean }>`
  background: none;
  border: none;
  color: ${({ $active }) => ($active ? "#ffe600" : "#555")};
  font-size: 22px;
  cursor: ${({ $active }) => ($active ? "pointer" : "default")};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, color 0.2s ease;

  &:hover {
    transform: ${({ $active }) => ($active ? "scale(1.1)" : "none")};
    color: ${({ $active }) => ($active ? "#ffed33" : "#555")};
  }
`;

const TriggerButton = styled.button`
  background: #232428;
  border: 1px solid #3a3a3a;
  border-radius: 8px;
  padding: 6px 10px;
  margin-bottom: 10px;
  color: #ddd;
  font-size: 13px;
  cursor: pointer;
  transition: 0.2s;

  &:hover {
    background: #2d2f33;
  }
`;

const ButtonsContainer = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: nowrap;
  justify-content: flex-start;

  /* Só aplica margin se realmente tiver botões */
  &:empty {
    margin-bottom: 0;
  }

  &:not(:empty) {
    margin-bottom: 8px;
  }
`;
