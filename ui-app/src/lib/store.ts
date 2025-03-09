import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  role: 'user' | 'admin';
}

interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface Agent {
  id: string;
  name: string;
  type: string;
  config: Record<string, any>;
}

interface Chain {
  id: string;
  name: string;
  nodes: any[];
  edges: any[];
}

interface AgentState {
  agents: Agent[];
  chains: Chain[];
  addChain: (chain: Omit<Chain, 'id'>) => void;
  updateAgent: (id: string, updates: Partial<Agent>) => void;
}

// Dummy users for testing
const USERS = [
  { id: '1', email: 'admin@example.com', password: 'admin123', role: 'admin' as const },
  { id: '2', email: 'user@example.com', password: 'user123', role: 'user' as const }
];

export const useAuth = create<AuthState>((set) => ({
  user: null,
  login: async (email: string, password: string) => {
    const user = USERS.find(u => u.email === email && u.password === password);
    if (user) {
      const { password: _, ...userWithoutPassword } = user;
      set({ user: userWithoutPassword });
    } else {
      throw new Error('Invalid credentials');
    }
  },
  logout: () => set({ user: null })
}));

export const useAgentStore = create<AgentState>((set) => ({
  agents: [
    {
      id: '1',
      name: 'Document Summarizer',
      type: 'summarizer',
      config: {
        model: 'gpt-4',
        maxTokens: 500
      }
    },
    {
      id: '2',
      name: 'Email Agent',
      type: 'email',
      config: {
        smtp: 'smtp.example.com',
        port: 587
      }
    },
    {
      id: '3',
      name: 'Salesforce Agent',
      type: 'sfdc',
      config: {
        instance: 'https://login.salesforce.com',
        version: '54.0'
      }
    }
  ],
  chains: [],
  addChain: (chain) => set((state) => ({
    chains: [...state.chains, { ...chain, id: `chain-${Date.now()}` }]
  })),
  updateAgent: (id, updates) => set((state) => ({
    agents: state.agents.map(agent =>
      agent.id === id ? { ...agent, ...updates } : agent
    )
  }))
}));
