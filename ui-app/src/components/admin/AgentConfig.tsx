import React, { useState } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Settings2, GitBranch, Pencil } from 'lucide-react';
import { useAgentStore } from '@/lib/store';
import { WorkflowBuilder } from './WorkflowBuilder';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

interface ConfigField {
  key: string;
  value: any;
  type: 'string' | 'number';
}

function AgentConfigDialog({ agent }: { agent: any }) {
  const updateAgent = useAgentStore(state => state.updateAgent);
  const [config, setConfig] = useState<ConfigField[]>(
    Object.entries(agent.config).map(([key, value]) => ({
      key,
      value,
      type: typeof value === 'number' ? 'number' : 'string'
    }))
  );
  const [name, setName] = useState(agent.name);
  const [open, setOpen] = useState(false);

  const handleSave = () => {
    const newConfig = config.reduce((acc, field) => {
      acc[field.key] = field.type === 'number' ? Number(field.value) : field.value;
      return acc;
    }, {} as Record<string, any>);

    updateAgent(agent.id, {
      name,
      config: newConfig
    });
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button className="p-1 hover:bg-slate-100 rounded">
          <Pencil className="w-4 h-4 text-slate-600" />
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Edit Agent Configuration</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Agent Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm"
            />
          </div>
          <div className="space-y-4">
            <label className="text-sm font-medium">Configuration</label>
            {config.map((field, index) => (
              <div key={field.key} className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={field.key}
                  onChange={(e) => {
                    const newConfig = [...config];
                    newConfig[index].key = e.target.value;
                    setConfig(newConfig);
                  }}
                  className="px-3 py-2 border rounded-md text-sm"
                  placeholder="Key"
                />
                <input
                  type={field.type === 'number' ? 'number' : 'text'}
                  value={field.value}
                  onChange={(e) => {
                    const newConfig = [...config];
                    newConfig[index].value = e.target.value;
                    setConfig(newConfig);
                  }}
                  className="px-3 py-2 border rounded-md text-sm"
                  placeholder="Value"
                />
              </div>
            ))}
            <button
              onClick={() => setConfig([...config, { key: '', value: '', type: 'string' }])}
              className="text-sm text-indigo-600 hover:text-indigo-700"
            >
              + Add Field
            </button>
          </div>
        </div>
        <div className="flex justify-end gap-3">
          <button
            onClick={() => setOpen(false)}
            className="px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 rounded-md"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Save Changes
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function AgentConfig() {
  const agents = useAgentStore(state => state.agents);
  const chains = useAgentStore(state => state.chains);

  return (
    <div className="p-6">
      <Tabs defaultValue="workflow">
        <TabsList className="mb-4">
          <TabsTrigger value="agents" className="flex items-center gap-2">
            <Settings2 className="w-4 h-4" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="workflow" className="flex items-center gap-2">
            <GitBranch className="w-4 h-4" />
            Workflow Builder
          </TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-4">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="p-4 rounded-lg border bg-white hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-medium">{agent.name}</h3>
                <AgentConfigDialog agent={agent} />
              </div>
              <div className="text-sm text-slate-600">
                <p>Type: {agent.type}</p>
                <pre className="mt-2 p-2 bg-slate-100 rounded">
                  {JSON.stringify(agent.config, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </TabsContent>

        <TabsContent value="workflow" className="h-[calc(100vh-16rem)]">
          <div className="mb-4">
            <h2 className="text-lg font-medium mb-4">Existing Chains</h2>
            <div className="space-y-2">
              {chains.map((chain) => (
                <div key={chain.id} className="p-4 bg-white rounded-lg border">
                  <h3 className="font-medium text-slate-900">{chain.name}</h3>
                  <div className="mt-2 flex items-center gap-2">
                    {chain.nodes.map((node: any, index: number) => (
                      <React.Fragment key={node.id}>
                        <span className="px-3 py-1 bg-slate-100 rounded text-sm">
                          {node.data.label}
                        </span>
                        {index < chain.nodes.length - 1 && (
                          <span className="text-slate-400">→</span>
                        )}
                      </React.Fragment>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
          <WorkflowBuilder />
        </TabsContent>
      </Tabs>
    </div>
  );
}
