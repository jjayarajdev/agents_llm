import React from 'react';
import { ChatHistory } from './components/chat/ChatHistory';
import { AgentConfig } from './components/admin/AgentConfig';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';
import { MessageSquare, Settings, LogOut } from 'lucide-react';
import { LoginForm } from './components/auth/LoginForm';
import { useAuth } from './lib/store';

const dummyMessages = [
  {
    id: '1',
    content: 'Hello, I need help with document processing.',
    timestamp: '2024-03-10T10:00:00Z',
    sender: 'user'
  },
  {
    id: '2',
    content: 'I can help you with that. Please share your document.',
    timestamp: '2024-03-10T10:01:00Z',
    sender: 'agent'
  }
] as const;

function App() {
  const [selectedMessage, setSelectedMessage] = React.useState(dummyMessages[0]);
  const user = useAuth(state => state.user);
  const logout = useAuth(state => state.logout);

  if (!user) {
    return <LoginForm />;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-slate-900">Agent Management Console</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-600">{user.email}</span>
            <button
              onClick={logout}
              className="flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4">
        <div className="bg-white rounded-lg shadow-sm border">
          <Tabs defaultValue="chat" className="w-full">
            <TabsList className="w-full border-b px-4">
              <TabsTrigger value="chat" className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Chat History
              </TabsTrigger>
              {user.role === 'admin' && (
                <TabsTrigger value="config" className="flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Agent Configuration
                </TabsTrigger>
              )}
            </TabsList>

            <TabsContent value="chat">
              <div className="flex">
                <ChatHistory
                  messages={dummyMessages}
                  onSelectMessage={setSelectedMessage}
                />
                <div className="flex-1 p-6">
                  <div className="mb-4">
                    <span className="text-sm font-medium text-slate-500">
                      {new Date(selectedMessage.timestamp).toLocaleString()}
                    </span>
                    <h2 className="text-xl font-semibold mt-1">
                      Conversation Details
                    </h2>
                  </div>
                  <div className="bg-slate-50 rounded-lg p-4">
                    <p className="text-slate-700">{selectedMessage.content}</p>
                  </div>
                </div>
              </div>
            </TabsContent>

            {user.role === 'admin' && (
              <TabsContent value="config">
                <AgentConfig />
              </TabsContent>
            )}
          </Tabs>
        </div>
      </main>
    </div>
  );
}

export default App;
