export const API_URL = import.meta.env.VITE_API_URL;

export async function sendMessageToAPI(message: string, conversationId?: string) {
  const payload = {
    message,
    conversation_id: conversationId || null
  };

  const response = await fetch(`${API_URL}/api/v1/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Erro da API: ${errText}`);
  }

  return await response.json();
}
