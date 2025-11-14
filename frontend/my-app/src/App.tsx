import { useEffect, useState } from 'react';
import styled from 'styled-components';
import ChatContainer from './components/chat/ChatContainer';
import type { AutocompleteConfig } from './types/autocomplete';

function App() {
  const [hasMessages, setHasMessages] = useState(false);

  useEffect(() => {
    console.log("API URL:", import.meta.env.VITE_API_URL);
  }, []);

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
      <HeaderSection>
        <Title>
          <BoldWhite>Bem-vindo </BoldWhite>
          <NormalWhite>ao </NormalWhite>
          <Yellow>Agil.IA</Yellow>
        </Title>
        {!hasMessages && (
          <Subtitle>Seu assistente inteligente para insights ágeis e decisões mais rápidas.
            <br />
            Conectado ao Azure DevOps, o Agil.AI apoia PMOs no acompanhamento de projetos, análise de resultados e aumento da eficiência nas entregas, tudo em um só lugar!
          </Subtitle>
        )}
      </HeaderSection>

      <ChatWrapper $hasMessages={hasMessages}>
        <ChatContainer
          autocompleteConfigs={autocompleteConfigs}
          title=""
          onFirstMessage={() => setHasMessages(true)}
        />
      </ChatWrapper>
    </Container>
  );
}

export default App;

const Container = styled.div` 
  background: #0d0f12;
  height: 100vh;
  width: 100%;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  overflow: hidden;
  box-sizing: border-box;
  padding-top: 100px;
  position: relative;
`;

const HeaderSection = styled.div` 
  text-align: center; 
  margin: -20px auto 24px;
  max-width: 700px; 
`;

const Title = styled.h1` 
  font-size: 3rem; 
  font-weight: 700; 
  margin-bottom: 10px; 
`;

const BoldWhite = styled.span`
  color: white;
  font-weight: bold;
`;

const NormalWhite = styled.span`
  color: white;
  font-weight: normal;
`;

const Yellow = styled.span`
  color: #f7d404; 
  font-weight: bold;
`;

const Subtitle = styled.p` 
  font-size: 1.1rem; 
  color: #cfcfcf; 
  line-height: 1.5; 
`;

const ChatWrapper = styled.div<{ $hasMessages: boolean }>` 
  width: 100%;
  max-width: 800px;
  flex: 1;
  background: transparent;
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-top: ${({ $hasMessages }) => $hasMessages ? '20px' : '0'};
`;