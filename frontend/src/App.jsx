import { useState } from 'react';
import { api } from './api';
import SkillGraph from './components/SkillGraph';
import { Sparkles, Brain, ArrowRight } from 'lucide-react';

function App() {
  const [learnerId] = useState(`demo_${Math.random().toString(36).substring(7)}`);
  const [goal, setGoal] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [path, setPath] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!goal) return;
    
    setIsGenerating(true);
    try {
      const data = await api.createProfile(learnerId, {
        raw_goal_text: goal,
        known_skills: {},
        weekly_hours_available: 10
      });
      const pathData = await api.getPath(learnerId);
      setPath(pathData);
    } catch (err) {
      console.error(err);
      alert('Failed to generate path. Is the backend running?');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/30">
      {/* Navbar */}
      <header className="border-b bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-lg tracking-tight">
            <Brain className="w-6 h-6 text-primary" />
            <span>Path<span className="text-primary">AI</span></span>
          </div>
          {path && (
            <div className="text-sm font-medium opacity-70 bg-secondary/50 px-3 py-1 rounded-full">
              {path.steps.length} milestones • {path.total_estimated_hours}h estimated
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto p-6 flex flex-col relative">
        {/* Glow Effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-primary/20 blur-[120px] rounded-full pointer-events-none"></div>
        
        {!path ? (
          <div className="flex-1 flex flex-col items-center justify-center max-w-3xl mx-auto w-full animate-in fade-in zoom-in duration-700 pb-20 relative z-10">
            <div className="mb-8 p-5 bg-white/5 border border-white/10 rounded-full shadow-2xl backdrop-blur-md">
              <Sparkles className="w-10 h-10 text-primary animate-pulse" />
            </div>
            <h1 className="text-5xl md:text-7xl font-extrabold text-center tracking-tight mb-6 text-white drop-shadow-md">
              Master any skill,<br/>
              <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">pathways optimized by AI.</span>
            </h1>
            <p className="text-lg md:text-xl text-center text-white/70 mb-12 max-w-2xl leading-relaxed">
              Tell us your career goal. We'll generate a personalized, adapting curriculum grounded in a real prerequisite graph.
            </p>
            
            <form onSubmit={handleGenerate} className="w-full relative group">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full group-hover:bg-primary/30 transition-all duration-500 opacity-50"></div>
              <div className="relative flex items-center bg-card border shadow-xl rounded-full p-2 pl-6 overflow-hidden">
                <input 
                  type="text" 
                  className="flex-1 bg-transparent border-none outline-none text-lg text-white placeholder:text-white/50 h-12 w-full"
                  placeholder="e.g. I want to build highly scalable microservices..."
                  value={goal}
                  onChange={e => setGoal(e.target.value)}
                  disabled={isGenerating}
                />
                <button 
                  type="submit"
                  disabled={isGenerating || !goal}
                  className="bg-primary text-primary-foreground h-12 px-8 rounded-full font-bold flex items-center gap-2 hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:pointer-events-none disabled:hover:scale-100"
                >
                  {isGenerating ? 'Generating...' : 'Start Learning'}
                  {!isGenerating && <ArrowRight className="w-4 h-4" />}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="w-full h-[80vh] min-h-[600px] animate-in slide-in-from-bottom-8 duration-700 pb-6">
            <SkillGraph 
              path={path} 
              learnerId={learnerId} 
              onPathUpdate={setPath}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
