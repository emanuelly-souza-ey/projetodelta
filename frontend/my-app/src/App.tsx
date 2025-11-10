import { useState } from 'react';
import './App.css';
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
    <div className="App">
      <button
        onClick={() => setShowStorybook(!showStorybook)}
        style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          zIndex: 1000,
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        {showStorybook ? 'Show Chat' : 'Show Storybook'}
      </button>

      {showStorybook ? (
        <Storybook />
      ) : (
        <ChatContainer
          autocompleteConfigs={autocompleteConfigs}
          title="Chat Assistant"
        />
      )}
    </div>
  );
}

export default App;
