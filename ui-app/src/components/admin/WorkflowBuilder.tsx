import React, { useCallback, useState, DragEvent } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeProps,
  Handle,
  Position,
  Panel,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useAgentStore } from '@/lib/store';
import { Settings } from 'lucide-react';

interface AgentNodeData {
  label: string;
  type: string;
  config: Record<string, any>;
}

const AgentNode = ({ data }: NodeProps<AgentNodeData>) => {
  const [isConfiguring, setIsConfiguring] = useState(false);

  return (
    <div 
      className="px-4 py-2 shadow-lg rounded-md bg-white border border-gray-200 min-w-[200px]"
      onClick={() => setIsConfiguring(!isConfiguring)}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      <div className="flex items-center justify-between mb-2">
        <div className="font-medium text-sm">{data.label}</div>
        <Settings className="w-4 h-4 text-slate-400" />
      </div>
      <div className="text-xs text-slate-500 mb-2">{data.type}</div>
      {isConfiguring && data.config && (
        <div className="text-xs bg-slate-50 p-2 rounded">
          <pre className="whitespace-pre-wrap">
            {JSON.stringify(data.config, null, 2)}
          </pre>
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  );
};

const nodeTypes = {
  agent: AgentNode,
};

const AgentPalette = ({ agents }: { agents: any[] }) => {
  const onDragStart = (event: DragEvent<HTMLDivElement>, agent: any) => {
    event.dataTransfer.setData('application/json', JSON.stringify(agent));
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border w-64">
      <h4 className="text-sm font-medium mb-3">Available Agents</h4>
      <div className="space-y-2">
        {agents.map((agent) => (
          <div
            key={agent.id}
            draggable
            onDragStart={(e) => onDragStart(e, agent)}
            className="p-2 border rounded bg-slate-50 cursor-move hover:bg-slate-100 transition-colors"
          >
            <div className="font-medium text-sm">{agent.name}</div>
            <div className="text-xs text-slate-500">{agent.type}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const Flow = () => {
  const agents = useAgentStore(state => state.agents);
  const addChain = useAgentStore(state => state.addChain);
  const [chainName, setChainName] = useState('');
  const reactFlowInstance = useReactFlow();
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const reactFlowBounds = (event.target as Element)
        .closest('.react-flow')
        ?.getBoundingClientRect();

      if (!reactFlowBounds) return;

      const agentData = JSON.parse(
        event.dataTransfer.getData('application/json')
      );

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${agentData.id}-${++id}`,
        type: 'agent',
        position,
        data: {
          label: agentData.name,
          type: agentData.type,
          config: agentData.config,
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance, setNodes]
  );

  const onSave = useCallback(() => {
    if (!chainName.trim()) {
      alert('Please enter a chain name');
      return;
    }

    if (nodes.length < 2) {
      alert('Please add at least two agents to create a chain');
      return;
    }

    if (edges.length === 0) {
      alert('Please connect the agents to create a workflow');
      return;
    }

    const workflow = {
      name: chainName,
      nodes,
      edges,
    };

    addChain(workflow);

    // Reset form
    setChainName('');
    setEdges([]);
    setNodes([]);
  }, [nodes, edges, chainName, addChain]);

  return (
    <div className="h-full border rounded-lg bg-slate-50">
      <div className="h-12 flex items-center justify-between px-4 border-b bg-white">
        <h3 className="font-medium">Create New Chain</h3>
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={chainName}
            onChange={(e) => setChainName(e.target.value)}
            placeholder="Enter chain name"
            className="px-3 py-1 border rounded text-sm"
          />
          <button
            onClick={onSave}
            className="px-4 py-1 bg-indigo-600 text-white rounded-md text-sm hover:bg-indigo-700"
          >
            Save Chain
          </button>
        </div>
      </div>
      <div className="h-[calc(100%-3rem)] flex">
        <div className="p-4 border-r">
          <AgentPalette agents={agents} />
        </div>
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDragOver={onDragOver}
            onDrop={onDrop}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background />
            <Controls />
            <Panel position="top-left" className="bg-white p-4 rounded-lg shadow-sm border">
              <h4 className="text-sm font-medium mb-2">Instructions:</h4>
              <ul className="text-xs text-slate-600 space-y-1">
                <li>• Drag agents from the palette to the canvas</li>
                <li>• Connect agents by dragging between handles</li>
                <li>• Click agents to view/edit configuration</li>
                <li>• Enter chain name and save when done</li>
              </ul>
            </Panel>
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};

let id = 100;

export function WorkflowBuilder() {
  return (
    <ReactFlowProvider>
      <Flow />
    </ReactFlowProvider>
  );
}