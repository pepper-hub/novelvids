import React, { useState, useEffect, createContext, useContext, useRef } from 'react';
import { HashRouter as Router, Routes, Route, Link, useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  BookOpen, Layers, Clapperboard, Video, Plus, ChevronRight, Film, Settings,
  LayoutDashboard, Sparkles, FileText, User, Image as ImageIcon, Play,
  Trash2, Edit3, X, RefreshCw, Power, Loader2, Eye, EyeOff, MonitorPlay
} from 'lucide-react';
import { api } from './services/api';
import {
  AssetTypeEnum, TaskStatusEnum, VideoModelTypeEnum,
} from './types';
import type {
  Novel, Chapter, Asset, Scene, Video as VideoType, AiModelConfig, AiTask, AllEnums,
} from './types';

// --- Helpers ---

function sleep(ms: number): Promise<void> {
  return new Promise(r => setTimeout(r, ms));
}

async function pollTask(taskId: string): Promise<AiTask> {
  while (true) {
    await sleep(3000);
    const res = await api.getTask(taskId);
    const t = res.data;
    if (t.status === TaskStatusEnum.COMPLETED || t.status === TaskStatusEnum.FAILED || t.status === TaskStatusEnum.CANCELLED) {
      return t;
    }
  }
}

async function pollVideo(videoId: number): Promise<VideoType> {
  while (true) {
    await sleep(4000);
    const res = await api.queryVideo(videoId);
    const v = res.data;
    if (v.status === TaskStatusEnum.COMPLETED || v.status === TaskStatusEnum.FAILED) {
      return v;
    }
  }
}

function statusColor(status?: TaskStatusEnum): string {
  switch (status) {
    case TaskStatusEnum.COMPLETED: return 'bg-green-500/20 text-green-400';
    case TaskStatusEnum.PROCESSING: return 'bg-blue-500/20 text-blue-400';
    case TaskStatusEnum.PENDING: case TaskStatusEnum.QUEUED: return 'bg-yellow-500/20 text-yellow-400';
    case TaskStatusEnum.FAILED: return 'bg-red-500/20 text-red-400';
    case TaskStatusEnum.CANCELLED: return 'bg-gray-500/20 text-gray-400';
    default: return 'bg-gray-600 text-gray-300';
  }
}

function statusLabel(status?: TaskStatusEnum): string {
  switch (status) {
    case TaskStatusEnum.COMPLETED: return 'Completed';
    case TaskStatusEnum.PROCESSING: return 'Processing';
    case TaskStatusEnum.PENDING: return 'Pending';
    case TaskStatusEnum.QUEUED: return 'Queued';
    case TaskStatusEnum.FAILED: return 'Failed';
    case TaskStatusEnum.CANCELLED: return 'Cancelled';
    default: return 'Unknown';
  }
}

function modelLabel(type?: VideoModelTypeEnum): string {
  switch (type) {
    case VideoModelTypeEnum.VIDU_Q2: return 'Vidu Q2';
    case VideoModelTypeEnum.SORA_2: return 'Sora 2';
    case VideoModelTypeEnum.SEEDANCE: return 'Seedance';
    case VideoModelTypeEnum.VEO_3: return 'Veo 3';
    default: return 'Unknown';
  }
}

// --- Context ---

const EnumContext = createContext<AllEnums>({});
function useEnums() { return useContext(EnumContext); }

type ToastFn = (msg: string) => void;
const ToastContext = createContext<{ success: ToastFn; error: ToastFn }>({ success: () => {}, error: () => {} });
function useToast() { return useContext(ToastContext); }

const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<{ id: number; text: string; type: 'success' | 'error' }[]>([]);
  const nextId = useRef(0);

  function show(text: string, type: 'success' | 'error') {
    const id = nextId.current++;
    setToasts(prev => [...prev, { id, text, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }

  const ctx = {
    success: (msg: string) => show(msg, 'success'),
    error: (msg: string) => show(msg, 'error'),
  };

  return (
    <ToastContext.Provider value={ctx}>
      {children}
      <div className="fixed top-4 right-4 z-[100] space-y-2">
        {toasts.map(t => (
          <div key={t.id} className={`px-4 py-3 rounded-lg shadow-lg text-sm font-medium backdrop-blur-sm border animate-[slideIn_0.3s_ease] ${
            t.type === 'success' ? 'bg-green-500/20 text-green-300 border-green-500/30' : 'bg-red-500/20 text-red-300 border-red-500/30'
          }`}>
            {t.text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};

// --- Shared Components ---

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();
  const path = location.pathname;

  function navClass(target: string): string {
    const active = target === '/' ? path === '/' || path.startsWith('/novel') : path.startsWith(target);
    return active
      ? 'flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800 text-primary border border-gray-700/50'
      : 'flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-700 text-gray-300 hover:text-white transition-colors';
  }

  return (
    <div className="flex h-screen bg-background text-gray-100 overflow-hidden">
      <aside className="w-64 bg-surface border-r border-gray-700 flex flex-col">
        <div className="p-6 flex items-center gap-3 border-b border-gray-700">
          <div className="p-2 bg-gradient-to-tr from-primary to-secondary rounded-lg">
            <Clapperboard className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
            Cat Shadow
          </span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className={navClass('/')}>
            <BookOpen className="w-5 h-5" />
            Novels / Scripts
          </Link>
          <Link to="/videos" className={navClass('/videos')}>
            <MonitorPlay className="w-5 h-5" />
            Videos
          </Link>
          <div className="pt-4 pb-2 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            System
          </div>
          <Link to="/config" className={navClass('/config')}>
            <Settings className="w-5 h-5" />
            Model Config
          </Link>
        </nav>
      </aside>

      <main className="flex-1 overflow-auto bg-background relative">
        <div className="absolute top-0 left-0 w-full h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2"></div>
        {children}
      </main>
    </div>
  );
};

const Card: React.FC<{ children: React.ReactNode; className?: string; onClick?: () => void }> = ({ children, className = '', onClick }) => (
  <div onClick={onClick} className={`bg-surface border border-gray-700 rounded-xl p-5 shadow-lg hover:border-gray-600 transition-all ${className}`}>
    {children}
  </div>
);

const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' | 'ghost' }> = ({ children, className = '', variant = 'primary', ...props }) => {
  const variants = {
    primary: 'bg-gradient-to-r from-primary to-blue-600 hover:to-blue-500 text-white shadow-lg shadow-primary/20',
    secondary: 'bg-gray-700 hover:bg-gray-600 text-white',
    danger: 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20',
    ghost: 'bg-transparent hover:bg-white/5 text-gray-300',
  };
  return (
    <button className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
};

const Modal: React.FC<{ children: React.ReactNode; onClose: () => void }> = ({ children, onClose }) => (
  <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm" onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
    <Card className="w-[540px] max-h-[85vh] overflow-auto">
      {children}
    </Card>
  </div>
);

const StatusBadge: React.FC<{ status?: TaskStatusEnum }> = ({ status }) => (
  <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${statusColor(status)}`}>
    {statusLabel(status)}
  </span>
);

// --- Page: Dashboard ---

const Dashboard: React.FC = () => {
  const [novels, setNovels] = useState<Novel[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: '', author: '', description: '' });
  const toast = useToast();

  useEffect(() => { loadNovels(); }, []);

  async function loadNovels() {
    setLoading(true);
    try {
      const res = await api.getNovels();
      setNovels(res.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function handleCreate() {
    if (!form.name.trim()) return;
    try {
      await api.createNovel(form);
      setForm({ name: '', author: '', description: '' });
      setShowCreate(false);
      toast.success('Novel created');
      loadNovels();
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleDelete(e: React.MouseEvent, id: number) {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this novel and all its data?')) return;
    try {
      await api.deleteNovel(id);
      toast.success('Novel deleted');
      loadNovels();
    } catch (e: any) { toast.error((e as Error).message); }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">My Projects</h1>
          <p className="text-gray-400">Manage your novels and scripts</p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4" /> Create Project
        </Button>
      </header>

      {loading ? (
        <div className="text-center py-20 text-gray-500">Loading works...</div>
      ) : novels.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-700 rounded-xl">
          <BookOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">No projects yet.</p>
          <Button variant="ghost" onClick={() => setShowCreate(true)}>Create your first project</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
          {novels.map(novel => (
            <Link to={`/novel/${novel.id}`} key={novel.id}>
              <Card className="h-full group cursor-pointer hover:-translate-y-1">
                <div className="aspect-video bg-gray-800 rounded-lg mb-4 overflow-hidden relative">
                  {novel.cover ? (
                    <img src={novel.cover} alt={novel.name} className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                      <BookOpen className="w-10 h-10 text-gray-600" />
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                  <div className="absolute bottom-3 left-3">
                    <span className="px-2 py-1 bg-primary/20 text-primary text-xs rounded border border-primary/20 backdrop-blur-sm">
                      {novel.total_chapters ?? 0} Chapters
                    </span>
                  </div>
                  <button
                    onClick={e => handleDelete(e, novel.id)}
                    className="absolute top-2 right-2 p-1.5 bg-black/50 rounded-lg text-gray-400 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <h3 className="text-xl font-semibold text-white mb-1">{novel.name}</h3>
                <p className="text-sm text-gray-400">{novel.author || 'Unknown Author'}</p>
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{novel.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {showCreate && (
        <Modal onClose={() => setShowCreate(false)}>
          <h2 className="text-xl font-bold text-white mb-4">New Project</h2>
          <div className="space-y-4">
            <input
              className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
              placeholder="Novel Name *"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
            <input
              className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
              placeholder="Author"
              value={form.author}
              onChange={e => setForm(f => ({ ...f, author: e.target.value }))}
            />
            <textarea
              className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
              placeholder="Description"
              rows={3}
              value={form.description}
              onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            />
          </div>
          <div className="flex justify-end gap-2 mt-6">
            <Button variant="ghost" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button onClick={handleCreate}>Create</Button>
          </div>
        </Modal>
      )}
    </div>
  );
};

// --- Page: Novel Detail ---

const NovelDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();
  const [novel, setNovel] = useState<Novel | null>(null);
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [loading, setLoading] = useState(true);
  const [splitting, setSplitting] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', author: '', description: '', content: '' });

  useEffect(() => { if (id) loadData(parseInt(id)); }, [id]);

  async function loadData(novelId: number) {
    setLoading(true);
    try {
      const [novelRes, chapterRes] = await Promise.all([
        api.getNovel(novelId),
        api.getChapters(novelId),
      ]);
      setNovel(novelRes.data);
      setChapters(chapterRes.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  function openEdit() {
    if (!novel) return;
    setEditForm({
      name: novel.name,
      author: novel.author || '',
      description: novel.description || '',
      content: novel.content || '',
    });
    setShowEdit(true);
  }

  async function handleSave() {
    if (!novel) return;
    try {
      const res = await api.updateNovel(novel.id, editForm);
      setNovel(res.data);
      setShowEdit(false);
      toast.success('Novel updated');
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleSplit() {
    if (!novel) return;
    setSplitting(true);
    try {
      await api.splitNovel(novel.id);
      toast.success('Chapters created');
      await loadData(novel.id);
    } catch (e: any) { toast.error(e.message); }
    setSplitting(false);
  }

  async function handleDeleteNovel() {
    if (!novel || !confirm('Delete this novel and all its data?')) return;
    try {
      await api.deleteNovel(novel.id);
      toast.success('Novel deleted');
      navigate('/');
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleDeleteChapter(e: React.MouseEvent, chId: number) {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('Delete this chapter?')) return;
    try {
      await api.deleteChapter(chId);
      toast.success('Chapter deleted');
      if (novel) loadData(novel.id);
    } catch (e: any) { toast.error((e as Error).message); }
  }

  if (loading) return <div className="p-10 text-center text-gray-400">Loading Project...</div>;
  if (!novel) return <div className="p-10 text-center text-red-400">Novel not found</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="bg-surface border-b border-gray-700 p-8 shadow-sm">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
            <Link to="/" className="hover:text-white">Dashboard</Link>
            <ChevronRight className="w-4 h-4" />
            <span className="text-white">{novel.name}</span>
          </div>
          <div className="flex justify-between items-end">
            <div className="flex gap-6">
              <div className="w-24 h-36 rounded-lg shadow-lg border border-gray-600 overflow-hidden bg-gray-800 flex-shrink-0">
                {novel.cover ? (
                  <img src={novel.cover} className="w-full h-full object-cover" alt="Cover" />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                    <BookOpen className="w-8 h-8 text-gray-600" />
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">{novel.name}</h1>
                <p className="text-gray-400 mb-4 max-w-2xl">{novel.description || 'No description'}</p>
                <div className="flex gap-4 text-sm text-gray-500">
                  <span>Author: {novel.author || 'Unknown'}</span>
                  <span>Created: {new Date(novel.created_at).toLocaleDateString()}</span>
                  <span>Content: {novel.content ? `${novel.content.length} chars` : 'Empty'}</span>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="ghost" onClick={openEdit}><Edit3 className="w-4 h-4" /> Edit</Button>
              <Button variant="danger" onClick={handleDeleteNovel}><Trash2 className="w-4 h-4" /></Button>
              <Button variant="secondary" onClick={handleSplit} disabled={splitting}>
                {splitting ? <><Loader2 className="w-4 h-4 animate-spin" /> Splitting...</> : <><Sparkles className="w-4 h-4" /> Auto Split Chapters</>}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <FileText className="w-5 h-5 text-primary" />
            Chapters ({chapters.length})
          </h2>

          {chapters.length === 0 ? (
            <div className="text-center py-20 border-2 border-dashed border-gray-700 rounded-xl">
              <p className="text-gray-500 mb-4">No chapters yet. {!novel.content && 'Edit the novel to add content first, then split.'}</p>
              {novel.content && <Button variant="ghost" onClick={handleSplit}>Use AI to split novel content</Button>}
            </div>
          ) : (
            <div className="grid gap-4">
              {chapters.map(chapter => (
                <Link to={`/novel/${novel.id}/chapter/${chapter.id}/step/1`} key={chapter.id}>
                  <div className="bg-surface/50 border border-gray-700/50 p-4 rounded-lg flex justify-between items-center hover:bg-gray-700/50 transition-colors group">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 font-mono text-sm border border-gray-700">
                        {chapter.number}
                      </div>
                      <div>
                        <h3 className="font-medium text-white group-hover:text-primary transition-colors">{chapter.name}</h3>
                        <div className="flex gap-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${(chapter.workflow_status ?? 0) >= 3 ? 'bg-green-500/20 text-green-400' : 'bg-gray-600 text-gray-300'}`}>
                            {(chapter.workflow_status ?? 0) >= 3 ? 'Entities Ready' : 'Pending Extract'}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${(chapter.workflow_status ?? 0) >= 4 ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-600 text-gray-300'}`}>
                            {(chapter.workflow_status ?? 0) >= 4 ? 'Storyboard Ready' : 'No Storyboard'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={e => handleDeleteChapter(e, chapter.id)}
                        className="p-2 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                      <div className="flex items-center gap-2 text-gray-500 group-hover:text-white">
                        <span className="text-sm">Enter Workflow</span>
                        <ChevronRight className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {showEdit && (
        <Modal onClose={() => setShowEdit(false)}>
          <h2 className="text-xl font-bold text-white mb-4">Edit Novel</h2>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Name</label>
              <input
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                value={editForm.name}
                onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Author</label>
              <input
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                value={editForm.author}
                onChange={e => setEditForm(f => ({ ...f, author: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Description</label>
              <textarea
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                rows={2}
                value={editForm.description}
                onChange={e => setEditForm(f => ({ ...f, description: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Content</label>
              <textarea
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none font-mono text-sm"
                rows={12}
                placeholder="Paste the full novel text here..."
                value={editForm.content}
                onChange={e => setEditForm(f => ({ ...f, content: e.target.value }))}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-6">
            <Button variant="ghost" onClick={() => setShowEdit(false)}>Cancel</Button>
            <Button onClick={handleSave}>Save</Button>
          </div>
        </Modal>
      )}
    </div>
  );
};

// --- Workflow Components ---

const StepIndicator: React.FC<{ currentStep: number; novelId: string; chapterId: string }> = ({ currentStep, novelId, chapterId }) => {
  const steps = [
    { id: 1, name: 'Extraction', icon: User },
    { id: 2, name: 'Assets', icon: ImageIcon },
    { id: 3, name: 'Storyboard', icon: Layers },
    { id: 4, name: 'Studio', icon: Film },
  ];

  return (
    <div className="w-64 bg-surface border-r border-gray-700 p-4 flex flex-col gap-2">
      <Link to={`/novel/${novelId}`} className="mb-2 flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors px-2">
        <ChevronRight className="w-4 h-4 rotate-180" /> Back to Novel
      </Link>
      <div className="mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider px-2">Workflow Steps</div>
      {steps.map(step => (
        <Link to={`/novel/${novelId}/chapter/${chapterId}/step/${step.id}`} key={step.id}>
          <div className={`flex items-center gap-3 px-3 py-3 rounded-lg transition-all ${currentStep === step.id ? 'bg-primary/10 text-primary border border-primary/20' : 'text-gray-400 hover:bg-gray-700/50'}`}>
            <step.icon className="w-4 h-4" />
            <span className="font-medium text-sm">{step.name}</span>
          </div>
        </Link>
      ))}
    </div>
  );
};

// Step 1: Extract
const StepExtraction: React.FC<{ chapterId: number; novelId: number }> = ({ chapterId, novelId }) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const toast = useToast();

  useEffect(() => { loadAssets(); }, [chapterId]);

  async function loadAssets() {
    setLoading(true);
    try {
      const res = await api.getAssets(novelId);
      setAssets(res.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function handleExtract() {
    setExtracting(true);
    try {
      const res = await api.extractEntities(chapterId);
      toast.success('Extraction started, polling...');
      const task = await pollTask(res.data.id);
      if (task.status === TaskStatusEnum.COMPLETED) {
        toast.success('Extraction completed');
      } else {
        toast.error('Extraction failed');
      }
      await loadAssets();
    } catch (e: any) { toast.error(e.message); }
    setExtracting(false);
  }

  function renderAssetList(type: AssetTypeEnum, title: string) {
    const items = assets.filter(a => a.asset_type === type);
    return (
      <div className="mb-8">
        <h3 className="text-md font-semibold text-gray-300 mb-3 border-l-4 border-primary pl-3">{title}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.length === 0 && <div className="text-sm text-gray-500 italic p-2">No items found.</div>}
          {items.map(item => (
            <Card key={item.id} className="p-4 flex items-start gap-4">
              <div className="w-12 h-12 rounded bg-gray-700 flex-shrink-0 flex items-center justify-center overflow-hidden">
                {item.main_image ? (
                  <img src={item.main_image} className="w-full h-full object-cover" alt={item.canonical_name} />
                ) : (
                  <span className="text-xs text-gray-500">{type === AssetTypeEnum.PERSON ? 'Role' : type === AssetTypeEnum.SCENE ? 'Scene' : 'Item'}</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-bold text-white text-sm">{item.canonical_name}</h4>
                {item.aliases && item.aliases.length > 0 && (
                  <p className="text-xs text-gray-500 mt-0.5">aka: {item.aliases.join(', ')}</p>
                )}
                <p className="text-xs text-gray-400 mt-1 line-clamp-2">{item.description}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Entity Extraction</h2>
          <p className="text-gray-400 text-sm">Analyze chapter content to identify characters, scenes, and items.</p>
        </div>
        <Button onClick={handleExtract} disabled={extracting}>
          {extracting ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</> : <><Sparkles className="w-4 h-4" /> Auto Extract</>}
        </Button>
      </div>

      {loading ? <div className="text-center py-10 text-gray-500">Loading...</div> : (
        <div className="space-y-6">
          {renderAssetList(AssetTypeEnum.PERSON, 'Characters')}
          {renderAssetList(AssetTypeEnum.SCENE, 'Scenes')}
          {renderAssetList(AssetTypeEnum.ITEM, 'Items')}
        </div>
      )}
    </div>
  );
};

// Step 2: Assets
const StepAssets: React.FC<{ chapterId: number; novelId: number }> = ({ chapterId, novelId }) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => { loadAssets(); }, [chapterId]);

  async function loadAssets() {
    setLoading(true);
    try {
      const res = await api.getAssets(novelId);
      setAssets(res.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function generateImage(asset: Asset) {
    setProcessingId(asset.id);
    try {
      const res = await api.generateAssetImage(asset.id);
      toast.success('Image generation started...');
      const task = await pollTask(res.data.id);
      if (task.status === TaskStatusEnum.COMPLETED) {
        toast.success('Image generated');
      } else {
        toast.error('Image generation failed');
      }
      await loadAssets();
    } catch (e: any) { toast.error(e.message); }
    setProcessingId(null);
  }

  if (loading) return <div className="p-10 text-center text-gray-500">Loading...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">Visual Assets</h2>
        <p className="text-gray-400 text-sm">Generate visual references (concept art) for extracted entities.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {assets.map(asset => (
          <Card key={asset.id} className="p-0 overflow-hidden group">
            <div className="aspect-square bg-gray-800 relative">
              {asset.main_image ? (
                <img src={asset.main_image} className="w-full h-full object-cover" alt={asset.canonical_name} />
              ) : (
                <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                  <ImageIcon className="w-8 h-8" />
                </div>
              )}
              <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2">
                <Button onClick={() => generateImage(asset)} disabled={processingId === asset.id} className="text-sm">
                  {processingId === asset.id ? <><Loader2 className="w-3 h-3 animate-spin" /> Gen...</> : (asset.main_image ? 'Regenerate' : 'Generate')}
                </Button>
              </div>
            </div>
            <div className="p-3 bg-surface border-t border-gray-700">
              <h4 className="font-bold text-sm text-white truncate">{asset.canonical_name}</h4>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-gray-500 uppercase">{asset.asset_type === AssetTypeEnum.PERSON ? 'Character' : asset.asset_type === AssetTypeEnum.SCENE ? 'Scene' : 'Prop'}</span>
                {asset.main_image && <span className="w-2 h-2 rounded-full bg-green-500"></span>}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Step 3: Storyboard
const StepStoryboard: React.FC<{ chapterId: number }> = ({ chapterId }) => {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editPrompt, setEditPrompt] = useState('');
  const toast = useToast();

  useEffect(() => { loadScenes(); }, [chapterId]);

  async function loadScenes() {
    setLoading(true);
    try {
      const res = await api.getScenes(chapterId);
      setScenes(res.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function handleGenerate() {
    setGenerating(true);
    try {
      const res = await api.generateScenes({ chapter_id: chapterId });
      toast.success('Scene generation started...');
      const task = await pollTask(res.data.id);
      if (task.status === TaskStatusEnum.COMPLETED) {
        toast.success('Scenes generated');
      } else {
        toast.error('Scene generation failed');
      }
      await loadScenes();
    } catch (e: any) { toast.error(e.message); }
    setGenerating(false);
  }

  async function handleSavePrompt(sceneId: number) {
    try {
      await api.patchScene(sceneId, { prompt: editPrompt });
      toast.success('Prompt saved');
      setEditingId(null);
      loadScenes();
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleDeleteScene(sceneId: number) {
    if (!confirm('Delete this scene?')) return;
    try {
      await api.deleteScene(sceneId);
      toast.success('Scene deleted');
      loadScenes();
    } catch (e: any) { toast.error(e.message); }
  }

  if (loading) return <div className="p-10 text-center text-gray-500">Loading...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">Storyboard</h2>
          <p className="text-gray-400 text-sm">Break down the chapter into shots and scenes.</p>
        </div>
        <Button onClick={handleGenerate} disabled={generating}>
          {generating ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating...</> : <><Sparkles className="w-4 h-4" /> Generate Scenes</>}
        </Button>
      </div>

      <div className="space-y-4">
        {scenes.map(scene => (
          <div key={scene.id} className="flex gap-4 p-4 bg-surface border border-gray-700 rounded-lg hover:border-primary/50 transition-colors">
            <div className="flex-shrink-0 w-16 text-center">
              <span className="block text-2xl font-bold text-gray-600">#{scene.sequence}</span>
              <span className="text-xs text-gray-500">{scene.duration ?? 0}s</span>
            </div>
            <div className="flex-1">
              <h4 className="text-white font-medium mb-1">{scene.description}</h4>
              {editingId === scene.id ? (
                <div className="space-y-2">
                  <textarea
                    className="w-full bg-gray-900 border border-gray-700 rounded p-3 text-sm text-gray-300 focus:border-primary outline-none font-mono"
                    rows={3}
                    value={editPrompt}
                    onChange={e => setEditPrompt(e.target.value)}
                  />
                  <div className="flex gap-2">
                    <Button className="text-xs px-3 py-1" onClick={() => handleSavePrompt(scene.id)}>Save</Button>
                    <Button variant="ghost" className="text-xs px-3 py-1" onClick={() => setEditingId(null)}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <div className="bg-gray-900/50 p-3 rounded text-sm text-gray-400 font-mono border border-gray-800">
                  {scene.prompt || 'No prompt yet'}
                </div>
              )}
              {scene.assets && scene.assets.length > 0 && (
                <div className="flex gap-1.5 mt-2">
                  {scene.assets.map(a => (
                    <span key={a.id} className="text-xs px-2 py-0.5 bg-primary/10 text-primary rounded border border-primary/20">
                      @{a.canonical_name}
                    </span>
                  ))}
                </div>
              )}
            </div>
            <div className="flex flex-col gap-2 justify-center">
              <Button variant="ghost" className="p-2" onClick={() => { setEditingId(scene.id); setEditPrompt(scene.prompt || ''); }}>
                <Edit3 className="w-4 h-4" />
              </Button>
              <Button variant="ghost" className="p-2 text-red-400 hover:text-red-300" onClick={() => handleDeleteScene(scene.id)}>
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ))}
        {scenes.length === 0 && !generating && (
          <div className="text-center py-10 text-gray-500 border-2 border-dashed border-gray-700 rounded-xl">
            No scenes generated yet.
          </div>
        )}
      </div>
    </div>
  );
};

// Step 4: Studio
const StepStudio: React.FC<{ chapterId: number }> = ({ chapterId }) => {
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedModel, setSelectedModel] = useState<VideoModelTypeEnum>(VideoModelTypeEnum.VEO_3);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => { loadScenes(); }, [chapterId]);

  async function loadScenes() {
    setLoading(true);
    try {
      const res = await api.getScenes(chapterId);
      setScenes(res.data.items);
      if (res.data.items.length > 0 && !selectedScene) {
        handleSelectScene(res.data.items[0]);
      }
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function handleSelectScene(scene: Scene) {
    setSelectedScene(scene);
    setVideos([]);
    try {
      const res = await api.getVideos(1, 100, '-id', scene.id);
      setVideos(res.data.items);
    } catch { /* no videos yet */ }
  }

  async function handleGenerateVideo() {
    if (!selectedScene) return;
    setGenerating(true);
    try {
      const res = await api.generateVideo({ scene_id: selectedScene.id, model_type: selectedModel });
      const video = res.data;
      setVideos(prev => [video, ...prev]);
      toast.success('Video generation started...');
      const result = await pollVideo(video.id);
      setVideos(prev => prev.map(v => v.id === result.id ? result : v));
      if (result.status === TaskStatusEnum.COMPLETED) {
        toast.success('Video generated');
      } else {
        toast.error('Video generation failed');
      }
    } catch (e: any) { toast.error(e.message); }
    setGenerating(false);
  }

  async function handleRefreshVideo(videoId: number) {
    try {
      const res = await api.queryVideo(videoId);
      setVideos(prev => prev.map(v => v.id === res.data.id ? res.data : v));
    } catch (e: any) { toast.error(e.message); }
  }

  const latestVideo = videos.length > 0 ? videos[0] : null;

  if (loading) return <div className="p-10 text-center text-gray-500">Loading...</div>;

  return (
    <div className="flex h-full">
      {/* Scene List */}
      <div className="w-80 bg-surface border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700 font-bold text-gray-300">Scene List</div>
        <div className="flex-1 overflow-auto p-2 space-y-2">
          {scenes.map(scene => (
            <div
              key={scene.id}
              onClick={() => handleSelectScene(scene)}
              className={`p-3 rounded cursor-pointer border ${selectedScene?.id === scene.id ? 'bg-primary/10 border-primary text-white' : 'bg-gray-800 border-transparent text-gray-400 hover:bg-gray-700'}`}
            >
              <div className="flex justify-between mb-1">
                <span className="font-bold">Scene {scene.sequence}</span>
                <span className="text-xs opacity-50">{scene.duration ?? 0}s</span>
              </div>
              <div className="text-xs truncate">{scene.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Workbench */}
      <div className="flex-1 p-6 bg-background flex flex-col">
        {selectedScene ? (
          <>
            <div className="flex-1 flex flex-col items-center justify-center min-h-[400px] bg-black/40 rounded-lg border border-gray-800 mb-6 relative overflow-hidden">
              {latestVideo && latestVideo.status === TaskStatusEnum.COMPLETED && latestVideo.url ? (
                <div className="relative w-full h-full">
                  <video src={latestVideo.url} controls className="w-full h-full object-contain" />
                  <div className="absolute bottom-4 right-4 bg-black/70 text-white text-xs px-2 py-1 rounded">
                    {modelLabel(latestVideo.model_type)}
                  </div>
                </div>
              ) : latestVideo && (latestVideo.status === TaskStatusEnum.PROCESSING || latestVideo.status === TaskStatusEnum.PENDING || latestVideo.status === TaskStatusEnum.QUEUED) ? (
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <p className="text-primary animate-pulse">Generating Video...</p>
                  <p className="text-xs text-gray-500 mt-2">{modelLabel(latestVideo.model_type)} · {statusLabel(latestVideo.status)}</p>
                </div>
              ) : (
                <div className="text-gray-600 flex flex-col items-center">
                  <Film className="w-12 h-12 mb-2 opacity-50" />
                  <p>No video generated yet</p>
                </div>
              )}
            </div>

            {/* Controls */}
            <div className="bg-surface border border-gray-700 rounded-xl p-6">
              <div className="flex gap-4 mb-4">
                <div className="flex-1">
                  <label className="text-xs text-gray-500 uppercase font-bold mb-2 block">Prompt</label>
                  <div className="bg-gray-900 border border-gray-700 rounded p-3 text-sm text-gray-300 font-mono max-h-20 overflow-auto">
                    {selectedScene.prompt || 'No prompt'}
                  </div>
                </div>
                <div className="w-64 space-y-4">
                  <div>
                    <label className="text-xs text-gray-500 uppercase font-bold mb-2 block">Model</label>
                    <select
                      className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-sm text-white outline-none focus:border-primary"
                      value={selectedModel}
                      onChange={e => setSelectedModel(Number(e.target.value))}
                    >
                      <option value={VideoModelTypeEnum.VEO_3}>Veo 3 (High Quality)</option>
                      <option value={VideoModelTypeEnum.SORA_2}>Sora 2</option>
                      <option value={VideoModelTypeEnum.VIDU_Q2}>Vidu Q2</option>
                      <option value={VideoModelTypeEnum.SEEDANCE}>Seedance</option>
                    </select>
                  </div>
                  <Button className="w-full" onClick={handleGenerateVideo} disabled={generating}>
                    <Video className="w-4 h-4" />
                    {generating ? 'Generating...' : (latestVideo ? 'Regenerate Video' : 'Generate Video')}
                  </Button>
                </div>
              </div>

              {/* Video History */}
              {videos.length > 1 && (
                <div className="mt-4 border-t border-gray-700 pt-4">
                  <h4 className="text-xs text-gray-500 uppercase font-bold mb-2">History</h4>
                  <div className="flex gap-2 overflow-x-auto">
                    {videos.slice(1).map(v => (
                      <div key={v.id} className="flex-shrink-0 w-32 p-2 bg-gray-800 rounded-lg border border-gray-700 text-xs">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-gray-400">{modelLabel(v.model_type)}</span>
                          <button onClick={() => handleRefreshVideo(v.id)} className="text-gray-500 hover:text-white">
                            <RefreshCw className="w-3 h-3" />
                          </button>
                        </div>
                        <StatusBadge status={v.status} />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">Select a scene to start editing</div>
        )}
      </div>
    </div>
  );
};

const WorkflowLayout: React.FC = () => {
  const { novelId, chapterId, stepId } = useParams<{ novelId: string; chapterId: string; stepId: string }>();
  const currentStep = parseInt(stepId || '1');
  const nId = parseInt(novelId || '0');
  const cId = parseInt(chapterId || '0');

  return (
    <div className="flex h-full">
      <StepIndicator currentStep={currentStep} novelId={novelId!} chapterId={chapterId!} />
      <div className="flex-1 overflow-auto bg-gray-900/50">
        {currentStep === 1 && <StepExtraction chapterId={cId} novelId={nId} />}
        {currentStep === 2 && <StepAssets chapterId={cId} novelId={nId} />}
        {currentStep === 3 && <StepStoryboard chapterId={cId} />}
        {currentStep === 4 && <StepStudio chapterId={cId} />}
      </div>
    </div>
  );
};

// --- Page: Model Config ---

const ModelConfigPage: React.FC = () => {
  const [configs, setConfigs] = useState<AiModelConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState({ task_type: 4, name: '', base_url: '', api_key: '', model: '', concurrency: 1 });
  const [showKeys, setShowKeys] = useState<Record<number, boolean>>({});
  const toast = useToast();
  const enums = useEnums();

  const taskTypeLabels: Record<number, string> = { 1: 'Extract', 2: 'Ref Image', 3: 'Storyboard', 4: 'Video' };

  useEffect(() => { loadConfigs(); }, []);

  async function loadConfigs() {
    setLoading(true);
    try {
      const res = await api.getConfigs();
      setConfigs(res.data.items);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  function openCreate() {
    setEditId(null);
    setForm({ task_type: 4, name: '', base_url: '', api_key: '', model: '', concurrency: 1 });
    setShowForm(true);
  }

  function openEdit(c: AiModelConfig) {
    setEditId(c.id);
    setForm({
      task_type: c.task_type,
      name: c.name,
      base_url: c.base_url || '',
      api_key: c.api_key || '',
      model: c.model || '',
      concurrency: c.concurrency,
    });
    setShowForm(true);
  }

  async function handleSave() {
    try {
      if (editId) {
        await api.patchConfig(editId, form);
        toast.success('Config updated');
      } else {
        await api.createConfig(form);
        toast.success('Config created');
      }
      setShowForm(false);
      loadConfigs();
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleActivate(id: number) {
    try {
      await api.activateConfig(id);
      toast.success('Config activated');
      loadConfigs();
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this config?')) return;
    try {
      await api.deleteConfig(id);
      toast.success('Config deleted');
      loadConfigs();
    } catch (e: any) { toast.error(e.message); }
  }

  if (loading) return <div className="p-10 text-center text-gray-500">Loading...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Model Config</h1>
          <p className="text-gray-400">Manage AI model configurations for each task type</p>
        </div>
        <Button onClick={openCreate}>
          <Plus className="w-4 h-4" /> Add Config
        </Button>
      </header>

      {configs.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-700 rounded-xl">
          <Settings className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">No configurations yet.</p>
          <Button variant="ghost" onClick={openCreate}>Create your first config</Button>
        </div>
      ) : (
        <div className="space-y-3 relative z-10">
          {configs.map(c => (
            <div key={c.id} className="bg-surface border border-gray-700 rounded-lg p-4 flex items-center gap-4 hover:border-gray-600 transition-colors">
              <div className="flex-shrink-0">
                <div className={`w-3 h-3 rounded-full ${c.is_active ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-gray-600'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-bold text-white">{c.name}</h3>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/20">
                    {taskTypeLabels[c.task_type] || c.task_type}
                  </span>
                  {c.is_active && <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/20 text-green-400">Active</span>}
                </div>
                <div className="flex gap-4 text-sm text-gray-500">
                  <span>Model: {c.model || '-'}</span>
                  <span>URL: {c.base_url || '-'}</span>
                  <span className="flex items-center gap-1">
                    Key: {showKeys[c.id] ? (c.api_key || '-') : '••••••'}
                    <button onClick={() => setShowKeys(s => ({ ...s, [c.id]: !s[c.id] }))} className="text-gray-500 hover:text-white">
                      {showKeys[c.id] ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                    </button>
                  </span>
                  <span>Concurrency: {c.concurrency}</span>
                </div>
              </div>
              <div className="flex gap-2">
                {!c.is_active && (
                  <Button variant="ghost" className="p-2" onClick={() => handleActivate(c.id)} title="Activate">
                    <Power className="w-4 h-4 text-green-400" />
                  </Button>
                )}
                <Button variant="ghost" className="p-2" onClick={() => openEdit(c)}>
                  <Edit3 className="w-4 h-4" />
                </Button>
                <Button variant="ghost" className="p-2 text-red-400 hover:text-red-300" onClick={() => handleDelete(c.id)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <Modal onClose={() => setShowForm(false)}>
          <h2 className="text-xl font-bold text-white mb-4">{editId ? 'Edit Config' : 'New Config'}</h2>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Task Type</label>
              <select
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white outline-none focus:ring-2 focus:ring-primary"
                value={form.task_type}
                onChange={e => setForm(f => ({ ...f, task_type: Number(e.target.value) }))}
              >
                <option value={1}>Extract (Entity Extraction)</option>
                <option value={2}>Ref Image (Reference Image)</option>
                <option value={3}>Storyboard (Scene Generation)</option>
                <option value={4}>Video (Video Generation)</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Name</label>
              <input
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                placeholder="e.g. viduq2, veo3, gpt4o"
                value={form.name}
                onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Base URL</label>
              <input
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                placeholder="https://api.example.com"
                value={form.base_url}
                onChange={e => setForm(f => ({ ...f, base_url: e.target.value }))}
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">API Key</label>
              <input
                className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                placeholder="sk-..."
                type="password"
                value={form.api_key}
                onChange={e => setForm(f => ({ ...f, api_key: e.target.value }))}
              />
            </div>
            <div className="flex gap-4">
              <div className="flex-1">
                <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Model</label>
                <input
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                  placeholder="model-name"
                  value={form.model}
                  onChange={e => setForm(f => ({ ...f, model: e.target.value }))}
                />
              </div>
              <div className="w-32">
                <label className="text-xs text-gray-500 uppercase font-bold mb-1.5 block">Concurrency</label>
                <input
                  className="w-full bg-gray-800 border border-gray-600 rounded-lg p-3 text-white focus:ring-2 focus:ring-primary outline-none"
                  type="number"
                  min={1}
                  value={form.concurrency}
                  onChange={e => setForm(f => ({ ...f, concurrency: Number(e.target.value) }))}
                />
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-6">
            <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            <Button onClick={handleSave}>{editId ? 'Update' : 'Create'}</Button>
          </div>
        </Modal>
      )}
    </div>
  );
};

// --- Page: Videos ---

const VideosPage: React.FC = () => {
  const [videos, setVideos] = useState<VideoType[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const toast = useToast();

  useEffect(() => { loadVideos(); }, [page]);

  async function loadVideos() {
    setLoading(true);
    try {
      const res = await api.getVideos(page, 20, '-id');
      setVideos(res.data.items);
      setTotalPages(res.data.pagination.total_pages);
    } catch (e: any) { toast.error(e.message); }
    setLoading(false);
  }

  async function handleRefresh(id: number) {
    try {
      const res = await api.queryVideo(id);
      setVideos(prev => prev.map(v => v.id === res.data.id ? res.data : v));
      toast.success('Status refreshed');
    } catch (e: any) { toast.error(e.message); }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this video?')) return;
    try {
      await api.deleteVideo(id);
      toast.success('Video deleted');
      loadVideos();
    } catch (e: any) { toast.error(e.message); }
  }

  if (loading) return <div className="p-10 text-center text-gray-500">Loading...</div>;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="flex justify-between items-center mb-8 relative z-10">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Videos</h1>
          <p className="text-gray-400">All generated videos across projects</p>
        </div>
        <Button variant="secondary" onClick={loadVideos}><RefreshCw className="w-4 h-4" /> Refresh</Button>
      </header>

      {videos.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed border-gray-700 rounded-xl">
          <MonitorPlay className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-500">No videos yet. Generate videos from the Studio workflow.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 relative z-10">
            {videos.map(v => (
              <Card key={v.id} className="p-0 overflow-hidden group">
                <div className="aspect-video bg-gray-800 relative">
                  {v.status === TaskStatusEnum.COMPLETED && v.url ? (
                    <video src={v.url} className="w-full h-full object-cover" muted />
                  ) : v.status === TaskStatusEnum.PROCESSING || v.status === TaskStatusEnum.PENDING || v.status === TaskStatusEnum.QUEUED ? (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    </div>
                  ) : v.status === TaskStatusEnum.FAILED ? (
                    <div className="absolute inset-0 flex items-center justify-center text-red-400">
                      <X className="w-8 h-8" />
                    </div>
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-600">
                      <Film className="w-8 h-8" />
                    </div>
                  )}
                  <div className="absolute top-2 left-2">
                    <StatusBadge status={v.status} />
                  </div>
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {v.status !== TaskStatusEnum.COMPLETED && v.status !== TaskStatusEnum.FAILED && (
                      <button onClick={() => handleRefresh(v.id)} className="p-1.5 bg-black/50 rounded-lg text-gray-300 hover:text-white backdrop-blur-sm">
                        <RefreshCw className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button onClick={() => handleDelete(v.id)} className="p-1.5 bg-black/50 rounded-lg text-gray-300 hover:text-red-400 backdrop-blur-sm">
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
                <div className="p-4 bg-surface border-t border-gray-700">
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="text-sm font-medium text-white">Video #{v.id}</span>
                      <span className="text-xs text-gray-500 ml-2">Scene #{v.scene_id}</span>
                    </div>
                    <span className="text-xs px-2 py-0.5 rounded bg-secondary/20 text-secondary">
                      {modelLabel(v.model_type)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{new Date(v.created_at).toLocaleString()}</p>
                </div>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <Button variant="ghost" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
              <span className="px-4 py-2 text-gray-400 text-sm">Page {page} / {totalPages}</span>
              <Button variant="ghost" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// --- Main Router ---

const App: React.FC = () => {
  const [enums, setEnums] = useState<AllEnums>({});

  useEffect(() => {
    api.getEnums().then(res => setEnums(res.data)).catch(() => {});
  }, []);

  return (
    <EnumContext.Provider value={enums}>
      <ToastProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/novel/:id" element={<NovelDetail />} />
              <Route path="/novel/:novelId/chapter/:chapterId/step/:stepId" element={<WorkflowLayout />} />
              <Route path="/config" element={<ModelConfigPage />} />
              <Route path="/videos" element={<VideosPage />} />
            </Routes>
          </Layout>
        </Router>
      </ToastProvider>
    </EnumContext.Provider>
  );
};

export default App;
