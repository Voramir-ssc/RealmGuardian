import React, { useState, useEffect } from 'react';
import { CheckCircle2, Circle, Plus, Trash2, Calendar, Target, Clock, AlertCircle } from 'lucide-react';

const TaskManager = () => {
    const [tasks, setTasks] = useState([]);
    const [newTaskTitle, setNewTaskTitle] = useState('');
    const [newTaskType, setNewTaskType] = useState('daily');
    const [loading, setLoading] = useState(true);
    const apiUrl = import.meta.env.VITE_API_URL || `${window.location.protocol}//${window.location.hostname}:8000`;

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const res = await fetch(`${apiUrl}/api/user/tasks`);
            if (res.ok) {
                const data = await res.json();
                setTasks(data.tasks || []);
            }
        } catch (e) {
            console.error("Failed to fetch tasks", e);
        } finally {
            setLoading(false);
        }
    };

    const addTask = async (e) => {
        e.preventDefault();
        if (!newTaskTitle.trim()) return;

        try {
            const res = await fetch(`${apiUrl}/api/user/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: newTaskTitle, type: newTaskType })
            });

            if (res.ok) {
                const newTask = await res.json();
                setTasks([newTask, ...tasks]);
                setNewTaskTitle('');
            }
        } catch (e) {
            console.error("Failed to add task", e);
        }
    };

    const toggleTask = async (id, currentStatus) => {
        // Optimistic UI update
        setTasks(tasks.map(t => t.id === id ? { ...t, is_completed: !currentStatus } : t));

        try {
            await fetch(`${apiUrl}/api/user/tasks/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_completed: !currentStatus })
            });
        } catch (e) {
            console.error("Failed to toggle task", e);
            // Revert on error
            setTasks(tasks.map(t => t.id === id ? { ...t, is_completed: currentStatus } : t));
        }
    };

    const deleteTask = async (id) => {
        setTasks(tasks.filter(t => t.id !== id));
        try {
            await fetch(`${apiUrl}/api/user/tasks/${id}`, { method: 'DELETE' });
        } catch (e) {
            console.error("Failed to delete task", e);
            fetchTasks(); // Reload to fix state
        }
    };

    // Calculate monthly Trading Post progress
    const monthlyTasks = tasks.filter(t => t.type === 'monthly');
    const completedMonthlies = monthlyTasks.filter(t => t.is_completed).length;
    const progress = monthlyTasks.length > 0 ? (completedMonthlies / monthlyTasks.length) * 100 : 0;

    const renderTasks = (type) => {
        const filtered = tasks.filter(t => t.type === type);
        if (filtered.length === 0) return <div className="text-secondary/50 text-sm italic">Keine Aufgaben</div>;

        return filtered.map(task => (
            <div key={task.id} className="flex items-center gap-3 group py-2 border-b border-white/5 last:border-0 hover:bg-white/5 px-2 rounded -mx-2 transition-colors">
                <button 
                    onClick={() => toggleTask(task.id, task.is_completed)}
                    className="text-secondary hover:text-accent transition-colors"
                >
                    {task.is_completed ? <CheckCircle2 className="text-green-500" size={20} /> : <Circle size={20} />}
                </button>
                <span className={`text-sm flex-1 transition-all ${task.is_completed ? 'text-secondary/50 line-through' : 'text-secondary'}`}>
                    {task.title}
                </span>
                <button 
                    onClick={() => deleteTask(task.id)}
                    className="text-red-500/0 group-hover:text-red-500/50 hover:!text-red-500 transition-colors"
                >
                    <Trash2 size={16} />
                </button>
            </div>
        ));
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl overflow-hidden shadow-lg h-full flex flex-col">
            <div className="p-6 pb-4 border-b border-white/5 bg-gradient-to-r from-background/50 to-transparent">
                <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Target className="text-accent" size={20} />
                        Aktivitäten & To-Do
                    </h3>
                </div>
            </div>

            {/* Trading Post Progress */}
            {monthlyTasks.length > 0 && (
                <div className="p-4 bg-background/30 border-b border-white/5">
                    <div className="flex justify-between items-end mb-2">
                        <span className="text-xs font-medium text-amber-500 uppercase tracking-wider flex items-center gap-1">
                            <AlertCircle size={12} />
                            Handelsposten (Monatlich)
                        </span>
                        <span className="text-xs font-bold text-white">{completedMonthlies} / {monthlyTasks.length}</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-amber-500 rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]" 
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            <div className="p-6 flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-6">
                {/* Dailies */}
                <section>
                    <h4 className="text-accent text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Clock size={16} />
                        Tägliche Aufgaben (Dailies)
                    </h4>
                    {renderTasks('daily')}
                </section>

                {/* Weeklies */}
                <section>
                    <h4 className="text-purple-400 text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Calendar size={16} />
                        Wöchentliche Aufgaben (Weeklies)
                    </h4>
                    {renderTasks('weekly')}
                </section>

                {/* Monthlies list */}
                <section>
                    <h4 className="text-amber-500 text-sm font-semibold uppercase tracking-wider mb-3 flex items-center gap-2">
                        <AlertCircle size={16} />
                        Monatliche Aufgaben
                    </h4>
                    {renderTasks('monthly')}
                </section>
            </div>

            {/* Add Task Form */}
            <div className="p-4 border-t border-white/5 bg-background/50">
                <form onSubmit={addTask} className="flex gap-2">
                    <input 
                        type="text" 
                        value={newTaskTitle}
                        onChange={(e) => setNewTaskTitle(e.target.value)}
                        placeholder="Neue Aufgabe..." 
                        className="bg-background border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-accent flex-1"
                    />
                    <select 
                        value={newTaskType}
                        onChange={(e) => setNewTaskType(e.target.value)}
                        className="bg-background border border-white/10 rounded-lg px-2 py-2 text-sm text-secondary focus:outline-none focus:border-accent"
                    >
                        <option value="daily">Täglich</option>
                        <option value="weekly">Wöchentlich</option>
                        <option value="monthly">Monatlich</option>
                    </select>
                    <button type="submit" className="bg-accent/20 hover:bg-accent/40 text-accent p-2 rounded-lg transition-colors border border-accent/30">
                        <Plus size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default TaskManager;
