import { useState, useCallback } from 'react';
import ReactFlow, { 
  Controls, 
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { api } from '../api';
import { BookOpen, CheckCircle, Info, ChevronRight, X } from 'lucide-react';

const CustomNode = ({ data }) => {
  return (
    <div className={`px-4 py-3 shadow-lg rounded-xl border-2 min-w-[200px] transition-all
      ${data.status === 'locked' ? 'bg-muted border-muted-foreground/30 text-muted-foreground opacity-60' : 
        data.status === 'mastered' ? 'bg-primary/10 border-primary text-primary' : 
        'bg-card border-accent shadow-accent/20 cursor-pointer hover:scale-105'}`}>
      
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-bold uppercase tracking-wider opacity-70">
          {data.node.category}
        </span>
        {data.status === 'mastered' ? <CheckCircle className="w-4 h-4" /> : <BookOpen className="w-4 h-4 opacity-70" />}
      </div>
      
      <h3 className="font-semibold text-sm mb-1 leading-tight">{data.node.name}</h3>
      
      <div className="flex items-center gap-1 mt-2 text-[11px] opacity-70">
        <span className="flex gap-0.5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className={`w-1 h-3 rounded-sm ${i < data.node.difficulty_tier ? 'bg-current' : 'bg-current/20'}`} />
          ))}
        </span>
        <span className="ml-2">{data.node.resources.length} resources</span>
      </div>
    </div>
  );
};

const nodeTypes = { custom: CustomNode };

export default function SkillGraph({ path, learnerId, onPathUpdate }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [activeStep, setActiveStep] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const [score, setScore] = useState('');
  const [isAssessing, setIsAssessing] = useState(false);

  // Initialize graph from path data
  useState(() => {
    if (!path || !path.steps) return;
    
    const newNodes = [];
    const newEdges = [];
    
    // Auto-layout logic (simplified topological sort positioning)
    const levels = {};
    const processed = new Set();
    
    // Calculate depths
    path.steps.forEach(step => {
      let maxDepth = 0;
      step.skill.prerequisites.forEach(pre => {
        if (levels[pre] !== undefined) maxDepth = Math.max(maxDepth, levels[pre] + 1);
      });
      levels[step.skill.id] = maxDepth;
    });

    const levelCounts = {};
    
    const nodeIds = new Set(path.steps.map(s => s.skill.id));
    
    path.steps.forEach((step, idx) => {
      const depth = levels[step.skill.id] || 0;
      levelCounts[depth] = (levelCounts[depth] || 0) + 1;
      
      // Calculate X/Y positions
      const x = depth * 350;
      const y = (levelCounts[depth] - 1) * 150 - 50;

      // Status
      const status = step.is_unlocked ? 'unlocked' : 'locked';
      
      newNodes.push({
        id: step.skill.id,
        type: 'custom',
        position: { x, y },
        data: { node: step.skill, status, order: step.order },
      });

      step.skill.prerequisites.forEach(pre => {
        // ONLY create edge if the prerequisite node actually exists in this path!
        if (nodeIds.has(pre)) {
          newEdges.push({
            id: `${pre}-${step.skill.id}`,
            source: pre,
            target: step.skill.id,
            animated: status === 'unlocked',
            style: { stroke: status === 'unlocked' ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: status === 'unlocked' ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))' },
          });
        }
      });
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [path]);

  const onNodesChange = useCallback((chs) => setNodes((nds) => applyNodeChanges(chs, nds)), []);
  const onEdgesChange = useCallback((chs) => setEdges((eds) => applyEdgeChanges(chs, eds)), []);

  const onNodeClick = async (_, node) => {
    if (node.data.status === 'locked') return;
    
    setActiveStep(node);
    setExplanation(null);
    setIsExplaining(true);
    
    try {
      const data = await api.explainStep(learnerId, node.id);
      setExplanation(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsExplaining(false);
    }
  };

  const handleAssess = async () => {
    if (!score || !activeStep) return;
    setIsAssessing(true);
    try {
      const result = await api.assessStep(learnerId, activeStep.id, parseFloat(score) / 100);
      onPathUpdate(result.updated_path);
      setActiveStep(null);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAssessing(false);
    }
  };

  return (
    <div className="w-full h-full relative bg-background/50 backdrop-blur-sm rounded-xl border overflow-hidden shadow-2xl">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-dot-pattern"
      >
        <Background color="hsl(var(--muted-foreground))" gap={16} size={1} />
        <Controls className="bg-card border-accent fill-foreground" />
      </ReactFlow>

      {/* Slide-out Panel */}
      {activeStep && (
        <div className="absolute right-0 top-0 bottom-0 w-[400px] bg-card/95 backdrop-blur-xl border-l p-6 shadow-2xl flex flex-col transition-transform animate-in slide-in-from-right duration-300">
          <div className="flex justify-between items-start mb-6">
            <div>
              <span className="text-xs font-bold text-primary tracking-wider uppercase mb-1 block">Step {activeStep.data.order}</span>
              <h2 className="text-2xl font-bold">{activeStep.data.node.name}</h2>
            </div>
            <button onClick={() => setActiveStep(null)} className="p-2 hover:bg-muted rounded-full transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto pr-2 space-y-6">
            <div className="space-y-3">
              <h3 className="text-sm font-semibold flex items-center gap-2"><Info className="w-4 h-4 text-accent" /> Why this step?</h3>
              {isExplaining ? (
                <div className="h-24 bg-muted animate-pulse rounded-lg" />
              ) : explanation ? (
                <div className="bg-secondary/30 p-4 rounded-xl border border-secondary text-sm leading-relaxed text-secondary-foreground/90">
                  {explanation.explanation}
                </div>
              ) : null}
            </div>

            <div className="space-y-3">
              <h3 className="text-sm font-semibold">Resources</h3>
              <div className="grid gap-2">
                {activeStep.data.node.resources.map(res => (
                  <div key={res.id} className="p-3 rounded-lg border bg-background hover:border-primary/50 cursor-pointer transition-colors flex justify-between items-center group">
                    <div className="font-medium text-sm">{res.title}</div>
                    <ChevronRight className="w-4 h-4 opacity-50 group-hover:opacity-100 group-hover:text-primary transition-all" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t space-y-4">
            <h3 className="text-sm font-semibold">Record Assessment</h3>
            <div className="flex gap-2">
              <input 
                type="number" 
                placeholder="Score (0-100)" 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={score}
                onChange={e => setScore(e.target.value)}
              />
              <button 
                onClick={handleAssess}
                disabled={isAssessing || !score}
                className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
              >
                {isAssessing ? 'Saving...' : 'Submit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
