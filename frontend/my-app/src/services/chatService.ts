/**
 * Chat service for communicating with the backend API
 * Simple implementation: send message, receive response
 */

export interface ChatMessage {
    message: string;
    conversation_id?: string;

}

export interface ChatResponse {
    message: string;
    intent: string;
    confidence: number;
    data?: any;
    conversation_id: string;
    selected_project?: string;
    error?: string;
}

class ChatService {
    private readonly baseUrl: string;

    constructor() {
        // Use localhost:8000 as default for uvicorn backend
        this.baseUrl = 'http://localhost:8000/api/v1';
    }

    /**
     * Send message to chat endpoint
     * @param message - User message
     * @param conversationId - Optional conversation ID
     * @returns Promise with chat response
     */
    async sendMessage(message: string, conversationId?: string): Promise<ChatResponse> {
        try {
            const body: ChatMessage = {
                message,
                ...(conversationId && { conversation_id: conversationId })
            };

            const response = await fetch(`${this.baseUrl}/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    `Erro na requisição: ${response.status} - ${errorData.detail || 'Erro desconhecido'}`
                );
            }

            const data: ChatResponse = await response.json();
            return data;

        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`Falha ao conectar com o servidor: ${error.message}`);
            }
            throw new Error('Erro desconhecido na comunicação');
        }
    }

    /**
     * Clear conversation history
     * @param conversationId - Conversation ID to clear
     */
    async clearConversation(conversationId: string): Promise<void> {
        try {
            const response = await fetch(`${this.baseUrl}/chat/conversation/${conversationId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    `Erro ao limpar conversa: ${response.status} - ${errorData.detail || 'Erro desconhecido'}`
                );
            }
        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`Falha ao limpar conversa: ${error.message}`);
            }
            throw new Error('Erro desconhecido ao limpar conversa');
        }
    }

    /**
     * List all conversations
     */
    async listConversations(): Promise<{ conversations: string[], count: number }> {
        try {
            const response = await fetch(`${this.baseUrl}/chat/conversations`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    `Erro ao listar conversas: ${response.status} - ${errorData.detail || 'Erro desconhecido'}`
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`Falha ao listar conversas: ${error.message}`);
            }
            throw new Error('Erro desconhecido ao listar conversas');
        }
    }

    /**
     * Get team members
     * @param conversationId - Optional conversation ID for context
     */
    async getTeamMembers(conversationId?: string): Promise<{
        members: Array<{ id: string | null; name: string; email: string | null; role: string | null }>;
        total_count: number;
        message: string;
        conversation_id: string;
    }> {
        try {
            const url = conversationId
                ? `${this.baseUrl}/team/members?conversation_id=${conversationId}`
                : `${this.baseUrl}/team/members`;

            const response = await fetch(url);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    `Erro ao buscar membros: ${response.status} - ${errorData.detail || 'Erro desconhecido'}`
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`Falha ao buscar membros: ${error.message}`);
            }
            throw new Error('Erro desconhecido ao buscar membros');
        }
    }

    /**
     * Get projects
     * @param state - Optional state filter (Active, Closed, New)
     */
    async getProjects(state?: string): Promise<{
        projects: Array<{ id: number; name: string; state: string | null; description: string | null }>;
        total_count: number;
        message: string;
    }> {
        try {
            const url = state
                ? `${this.baseUrl}/projects/?state=${state}`
                : `${this.baseUrl}/projects/`;

            const response = await fetch(url);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    `Erro ao buscar projetos: ${response.status} - ${errorData.detail || 'Erro desconhecido'}`
                );
            }

            return await response.json();
        } catch (error) {
            if (error instanceof Error) {
                throw new Error(`Falha ao buscar projetos: ${error.message}`);
            }
            throw new Error('Erro desconhecido ao buscar projetos');
        }
    }
}

// Export singleton instance
export const chatService = new ChatService();
export default chatService;