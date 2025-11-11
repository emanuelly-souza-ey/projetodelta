import { useState } from 'react'; 
import styled from 'styled-components'; 
import ChatContainer from './components/chat/ChatContainer'; 
import Storybook from './pages/Storybook'; 
import { AutocompleteConfig } from './types/autocomplete'; 

function App() {
  const [showStorybook, setShowStorybook] = useState(false);

  const autocompleteConfigs: AutocompleteConfig[] = [
    {
      trigger: "@",
      items: ["Alice", "Bob", "Charlie", "Diana"],
      buttonLabel: "👤 Mention",
      onInsert: (user, msg) => {
        const lastAtIndex = msg.lastIndexOf("@");
        if (lastAtIndex !== -1) {
          const before = msg.slice(0, lastAtIndex);
          return `${before}@${user} `;
        }
        return `${msg}@${user} `;
      }
    },
    {
      trigger: "#",
      items: ["ProjectAlpha", "ProjectBeta", "ProjectGamma"],
      buttonLabel: "📁 Project",
      onInsert: (project, msg) => {
        const lastHashIndex = msg.lastIndexOf("#");
        if (lastHashIndex !== -1) {
          const before = msg.slice(0, lastHashIndex);
          return `${before}#${project} `;
        }
        return `${msg}#${project} `;
      }
    }
  ];

  return ( 
    <Container> 
      <FloatingButton onClick={() => setShowStorybook(!showStorybook)}> 
        {showStorybook ? 'Show Chat' : 'Show Storybook'} 
      </FloatingButton> 
      {!showStorybook && ( 
        <HeaderSection> 
          <Title>Agil.AI</Title> 
          <Subtitle> Texto de descrição do agente </Subtitle> 
        </HeaderSection> 
      )} 
      {showStorybook ? ( 
        <Storybook /> 
      ) : ( 
        <ChatWrapper> 
          <ChatContainer autocompleteConfigs={autocompleteConfigs} title="" /> 
        </ChatWrapper> 
      )} 
    </Container> 
  ); 
} 

export default App; 

const Container = styled.div` 
  background: #0d0f12; 
  min-height: 100vh; 
  height: auto;
  width: 100%; 
  overflow: visible;
  color: white; 
  padding: 40px 20px; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
`; 

const HeaderSection = styled.div` 
  text-align: center; 
  margin-bottom: 40px; 
  max-width: 700px; 
`; 

const Title = styled.h1` 
  font-size: 3.2rem; 
  font-weight: 700; 
  color: #f7d404; 
  margin-bottom: 12px; 
  text-align: center; 
`; 

const Subtitle = styled.p` 
  font-size: 1.2rem; 
  color: #d1d1d1; 
  line-height: 1.5; 
`; 

const ChatWrapper = styled.div` 
  width: 100%; 
  max-width: 900px; 
  max-height: 80vh;
  height: auto;
  overflow-y: auto;
  padding-right: 4px;
`; 

const FloatingButton = styled.button` 
  position: fixed; 
  top: 12px; 
  right: 12px; 
  z-index: 1000; 
  padding: 10px 20px; 
  background-color: #007bff; 
  color: white; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer; 
  font-size: 0.95rem; 
  transition: 0.2s ease; 
  &:hover { 
    background-color: #005ecb; 
  } 
`;