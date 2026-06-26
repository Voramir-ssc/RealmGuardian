/**
 * GoldOverviewWidget.jsx
 * 
 * Dashboard widget displaying total aggregated gold across all synced characters
 * and a summary of the connected Battle.net account status, including a sparkline/chart
 * for historical price trends similar to the TokenWidget.
 */
import React, { useState } from 'react';
import { Shield, Coins, Target, Edit2, Check, X, Trophy, Sparkles, Trash2 } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const GoldOverviewWidget = ({ characters = [], history = [], loading, tokenPrice = 0 }) => {
    const [goldRange, setGoldRange] = useState('all');

    // Goal State
    const [goalType, setGoalType] = useState(() => localStorage.getItem('rg_gold_goal_type') || 'none');
    const [goalValue, setGoalValue] = useState(() => Number(localStorage.getItem('rg_gold_goal_value')) || 0);
    const [goalName, setGoalName] = useState(() => localStorage.getItem('rg_gold_goal_name') || '');
    const [isEditing, setIsEditing] = useState(false);

    // Form temporary states
    const [tempType, setTempType] = useState(goalType);
    const [tempValue, setTempValue] = useState(goalValue);
    const [tempName, setTempName] = useState(goalName);

    // Calculate totals
    const totalGold = characters.reduce((acc, char) => acc + (char.gold || 0), 0);
    const tokenPriceGold = tokenPrice ? tokenPrice / 10000 : 0;
    const currentGold = totalGold / 10000;

    const saveGoal = () => {
        setGoalType(tempType);
        let finalVal = tempValue;
        if (tempType === 'token') {
            finalVal = tokenPriceGold;
        } else if (tempType === 'brutosaurier') {
            finalVal = 5000000;
        }
        setGoalValue(finalVal);
        setGoalName(tempName);
        localStorage.setItem('rg_gold_goal_type', tempType);
        localStorage.setItem('rg_gold_goal_value', finalVal.toString());
        localStorage.setItem('rg_gold_goal_name', tempName);
        setIsEditing(false);
    };

    const deleteGoal = () => {
        setGoalType('none');
        setGoalValue(0);
        setGoalName('');
        setTempType('none');
        setTempValue(0);
        setTempName('');
        localStorage.setItem('rg_gold_goal_type', 'none');
        localStorage.setItem('rg_gold_goal_value', '0');
        localStorage.setItem('rg_gold_goal_name', '');
        setIsEditing(false);
    };

    const cancelEdit = () => {
        setTempType(goalType);
        setTempValue(goalValue);
        setTempName(goalName);
        setIsEditing(false);
    };

    // Filter history based on range
    const getFilteredHistory = () => {
        const now = new Date();
        const safeHistory = Array.isArray(history) ? history : [];
        return safeHistory.filter(entry => {
            if (goldRange === 'all') return true;
            const entryDate = new Date(entry.timestamp);
            const diffTime = Math.abs(now - entryDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            if (goldRange === '7d') return diffDays <= 7;
            if (goldRange === '30d') return diffDays <= 30;
            return true;
        });
    };

    const filteredHistory = getFilteredHistory();

    // Format data for Recharts
    const chartData = filteredHistory.map(entry => {
        const date = new Date(entry.timestamp);
        return {
            date: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' }),
            fullDate: date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
            gold: Math.floor(entry.total_gold / 10000) // Convert copper to gold
        };
    });

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-surface/90 border border-white/10 rounded-lg p-3 shadow-xl backdrop-blur-md">
                    <p className="text-secondary text-xs mb-1">{payload[0].payload.fullDate}</p>
                    <p className="font-bold text-white">
                        {payload[0].value.toLocaleString('de-DE')} <span className="text-yellow-500 font-normal">g</span>
                    </p>
                </div>
            );
        }
        return null;
    };

    const tokensAffordable = tokenPriceGold > 0 ? Math.floor(currentGold / tokenPriceGold) : 0;
    const balanceValueEur = tokensAffordable * 13;

    let targetGold = 0;
    let goalLabel = '';
    if (goalType === 'token') {
        targetGold = tokenPriceGold;
        goalLabel = 'WoW Token';
    } else if (goalType === 'brutosaurier') {
        targetGold = 5000000;
        goalLabel = 'Karawanenbrutosaurier';
    } else if (goalType === 'custom') {
        targetGold = goalValue;
        goalLabel = goalName || 'Benutzerdefiniert';
    }

    const isGoalActive = goalType !== 'none' && targetGold > 0;
    const progressPercent = isGoalActive ? Math.min((currentGold / targetGold) * 100, 100) : 0;
    const isCompleted = isGoalActive && currentGold >= targetGold;
    const remainingGold = isGoalActive ? Math.max(targetGold - currentGold, 0) : 0;

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-yellow-500/30 transition-all duration-300 flex flex-col justify-between">
            <div className="flex justify-between items-start mb-2 relative z-10 w-full gap-4 flex-col sm:flex-row">
                <div className="flex-1 w-full">
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-1">Gesamtvermögen</h3>
                    <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-3xl font-bold text-white tracking-tight">{currentGold.toLocaleString('de-DE')}</span>
                        <span className="text-yellow-500 text-sm font-medium">Gold</span>
                    </div>
                    <div className="text-sm text-secondary/50 mt-1">
                        {characters.length > 0 ? `Auf ${characters.length} Charakteren` : 'Keine Daten'}
                    </div>
                    
                    <div className="flex flex-col md:flex-row gap-3 mt-3 w-full max-w-2xl">
                        {tokenPriceGold > 0 && (
                            <div className="p-2.5 rounded-xl bg-black/30 border border-white/5 text-xs text-secondary/80 flex flex-col gap-1 flex-1">
                                <div className="flex justify-between gap-4">
                                    <span>Gegenwert in Spielzeit:</span>
                                    <span className="font-semibold text-white truncate">{tokensAffordable} {tokensAffordable === 1 ? 'Token' : 'Tokens'}</span>
                                </div>
                                <div className="flex justify-between border-t border-white/5 pt-1 mt-0.5 gap-4">
                                    <span>Bnet-Guthabenwert:</span>
                                    <span className="font-semibold text-yellow-500 truncate">{balanceValueEur.toLocaleString('de-DE')},00 €</span>
                                </div>
                            </div>
                        )}

                        {/* Goal Tracker UI */}
                        <div className="p-2.5 rounded-xl bg-black/30 border border-white/5 flex flex-col justify-center flex-1 relative group/goal min-h-[58px]">
                            {isEditing ? (
                                <div className="flex flex-col gap-2 w-full">
                                    <div className="flex justify-between items-center text-[10px] font-semibold text-white/50">
                                        <span>SPARZIEL EINRICHTEN</span>
                                    </div>
                                    <div className="flex gap-1.5 items-center">
                                        <select
                                            value={tempType}
                                            onChange={(e) => {
                                                const val = e.target.value;
                                                setTempType(val);
                                                if (val === 'token') setTempValue(tokenPriceGold);
                                                else if (val === 'brutosaurier') setTempValue(5000000);
                                            }}
                                            className="bg-surface border border-white/10 rounded px-1.5 py-0.5 text-[11px] text-white flex-1 min-w-0"
                                        >
                                            <option value="none">Kein Sparziel</option>
                                            <option value="token">WoW Token (Live-Preis)</option>
                                            <option value="brutosaurier">Brutosaurier (5M g)</option>
                                            <option value="custom">Benutzerdefiniert...</option>
                                        </select>
                                        <div className="flex gap-1 shrink-0">
                                            {goalType !== 'none' && (
                                                <button onClick={deleteGoal} className="p-1 text-red-500 hover:text-red-400 hover:bg-white/5 rounded cursor-pointer transition-colors" title="Sparziel löschen">
                                                    <Trash2 size={14} />
                                                </button>
                                            )}
                                            <button onClick={saveGoal} className="p-1 text-green-500 hover:text-green-400 hover:bg-white/5 rounded cursor-pointer transition-colors" title="Speichern">
                                                <Check size={14} />
                                            </button>
                                            <button onClick={cancelEdit} className="p-1 text-secondary hover:text-white hover:bg-white/5 rounded cursor-pointer transition-colors" title="Abbrechen">
                                                <X size={14} />
                                            </button>
                                        </div>
                                    </div>
                                    {tempType === 'custom' && (
                                        <div className="flex flex-col gap-1.5 mt-0.5">
                                            <input
                                                type="text"
                                                value={tempName}
                                                onChange={(e) => setTempName(e.target.value)}
                                                placeholder="Name des Sparziels"
                                                className="bg-surface border border-white/10 rounded px-1.5 py-0.5 text-[11px] text-white w-full"
                                            />
                                            <input
                                                type="number"
                                                value={tempValue}
                                                onChange={(e) => setTempValue(Math.max(0, Number(e.target.value)))}
                                                placeholder="Goldmenge"
                                                className="bg-surface border border-white/10 rounded px-1.5 py-0.5 text-[11px] text-white w-full"
                                            />
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="w-full">
                                    <div className="flex justify-between items-center pr-5">
                                        <div className="flex items-center gap-1 text-[11px] text-secondary/80 font-medium">
                                            <Target size={12} className="text-accent" />
                                            <span>Ziel: {isGoalActive ? goalLabel : 'Keines'}</span>
                                        </div>
                                        <button
                                            onClick={() => {
                                                setTempType(goalType);
                                                setTempValue(goalValue);
                                                setIsEditing(true);
                                            }}
                                            className="opacity-0 group-hover/goal:opacity-100 p-1 text-secondary/60 hover:text-white transition-all cursor-pointer absolute right-2.5 top-2 rounded hover:bg-white/5"
                                            title="Ziel bearbeiten"
                                        >
                                            <Edit2 size={12} />
                                        </button>
                                    </div>

                                    {isGoalActive ? (
                                        <div className="space-y-1 mt-1">
                                            <div className="flex justify-between items-baseline text-[10px]">
                                                <span className="text-secondary/50 font-mono">
                                                    {Math.floor(currentGold).toLocaleString('de-DE')} / {Math.floor(targetGold).toLocaleString('de-DE')} g
                                                </span>
                                                <span className={`font-bold ${isCompleted ? 'text-green-400' : 'text-yellow-500'}`}>
                                                    {progressPercent.toFixed(1)}%
                                                </span>
                                            </div>

                                            {/* Progress Bar with Shimmer */}
                                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden relative border border-white/5">
                                                <div
                                                    className={`h-full rounded-full transition-all duration-500 relative ${
                                                        isCompleted
                                                            ? 'bg-gradient-to-r from-green-500 to-emerald-400 shadow-[0_0_8px_rgba(34,197,94,0.4)]'
                                                            : 'bg-gradient-to-r from-yellow-600 via-yellow-500 to-amber-400 shadow-[0_0_8px_rgba(234,179,8,0.4)]'
                                                    }`}
                                                    style={{ width: `${progressPercent}%` }}
                                                >
                                                    {!isCompleted && (
                                                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full animate-shimmer pointer-events-none" />
                                                    )}
                                                </div>
                                            </div>

                                            <div className="flex justify-between items-center text-[9px] text-secondary/60">
                                                {isCompleted ? (
                                                    <div className="flex items-center gap-0.5 text-green-400 font-semibold animate-pulse">
                                                        <Trophy size={10} />
                                                        <span>Erreicht! Meisterleistung! 🎉</span>
                                                    </div>
                                                ) : (
                                                    <span>Noch {Math.ceil(remainingGold).toLocaleString('de-DE')} g benötigt</span>
                                                )}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-[10px] text-secondary/40 italic flex items-center justify-between mt-1">
                                            <span>Kein Sparziel aktiv.</span>
                                            <button
                                                onClick={() => setIsEditing(true)}
                                                className="text-accent/80 hover:text-accent font-semibold not-italic cursor-pointer hover:underline"
                                            >
                                                Einrichten
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Range Filter Buttons */}
                <div className="flex bg-black/40 rounded-lg p-0.5 border border-white/5 shrink-0 z-20">
                    {['7d', '30d', 'all'].map((r) => (
                        <button
                            key={r}
                            onClick={() => setGoldRange(r)}
                            className={`px-2 py-1 text-[10px] font-semibold rounded-md transition-all ${
                                goldRange === r
                                    ? 'bg-yellow-500 text-black shadow-md'
                                    : 'text-white/40 hover:text-white/70'
                            }`}
                        >
                            {r === '7d' ? '7 Tage' : r === '30d' ? '30 Tage' : 'Gesamt'}
                        </button>
                    ))}
                </div>
            </div>

            <div className="h-32 w-full mt-auto opacity-75 group-hover:opacity-100 transition-opacity duration-500 relative z-10">
                {loading && filteredHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50 text-xs">
                        Verlauf wird geladen...
                    </div>
                ) : filteredHistory.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-secondary/50 text-xs">
                        Keine Daten im gewählten Zeitraum verfügbar.
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="goldGradientArea" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                            <XAxis
                                dataKey="date"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
                                dy={10}
                                minTickGap={20}
                            />
                            <YAxis
                                hide={true}
                                domain={['dataMin - 15000', 'dataMax + 15000']}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="gold"
                                stroke="#eab308"
                                strokeWidth={2}
                                fillOpacity={1}
                                fill="url(#goldGradientArea)"
                                animationDuration={1000}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                )}
            </div>

            <div className="mt-4 pt-4 border-t border-white/5 relative z-10 flex justify-between items-center">
                <div className="flex items-center gap-2 text-xs text-secondary/50">
                    <Shield size={12} />
                    <span>Battle.net Verbunden</span>
                </div>
                <div className="text-[10px] text-secondary/30 uppercase tracking-widest font-semibold">
                    Vermögensverlauf
                </div>
            </div>

            <div className="absolute top-0 right-0 p-3 opacity-5 pointer-events-none">
                <Coins size={120} />
            </div>
        </div>
    );
};

export default GoldOverviewWidget;
