import { useState } from 'react';
import { ChatLayout } from '@/components/ChatLayout';
import { ChatInterface, Message } from '@/components/ChatInterface';
import { useCompliance } from '@/hooks/useCompliance';

export default function Home() {
  const { loading, error, report, uploadContract, verifyCompliance, queryCompliance } = useCompliance();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'assistant',
      content: `Welcome to **Conformité AI**. I'm here to assist you with Mauritanian legal compliance.

Here's how I can help:
• **Analyze Statutes** (Statuts d'entreprise)
• **Review Work Contracts** (Contrats de travail)
• **Answer Queries** regarding the Code du Travail

To get started, simply **upload a document** (PDF/DOCX) using the attachment button below, or ask me a legal question directly.`,
      timestamp: new Date(),
    },
  ]);
  const [contractId, setContractId] = useState<string | null>(null);

  const handleSendMessage = async (content: string) => {
    if (!contractId || !content.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    try {
      const answer = await queryCompliance(contractId, content);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I encountered an error: ${err instanceof Error ? err.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      // Add loading message
      const uploadingMessage: Message = {
        id: Date.now().toString(),
        type: 'user',
        content: `📎 ${file.name}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, uploadingMessage]);

      // Upload and analyze
      const response = await uploadContract(file, 'statuts_entreprise');
      setContractId(response.contract_id);

      const analysisMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `✓ Document uploaded successfully!\n\n**Contract ID:** ${response.contract_id}\n\n📊 Analyzing for compliance issues...\n\nI'll review your document against Mauritanian labor law and corporate regulations. What would you like to know about this contract?`,
        timestamp: new Date(),
        report: report || undefined,
      };
      setMessages((prev) => [...prev, analysisMessage]);

      // Trigger verification
      await verifyCompliance(response.contract_id);
    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `❌ Error uploading document: ${err instanceof Error ? err.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  return (
    <ChatLayout>
      <ChatInterface
        messages={messages}
        onSendMessage={handleSendMessage}
        onFileUpload={handleFileUpload}
        loading={loading}
        error={error}
      />
    </ChatLayout>
  );
}
