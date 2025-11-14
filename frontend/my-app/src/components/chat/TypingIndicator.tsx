import styled, { keyframes } from "styled-components";

const TypingIndicator = () => {
    return (
        <Container>
            <Dot $delay="0s" />
            <Dot $delay="0.2s" />
            <Dot $delay="0.4s" />
        </Container>
    );
};

export default TypingIndicator;

const bounce = keyframes`
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 10px 14px;
`;

const Dot = styled.div<{ $delay: string }>`
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, #c6b200, #a89600);
  border-radius: 50%;
  animation: ${bounce} 1.4s ${props => props.$delay} infinite ease-in-out;
`;