import React, { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Landmark } from 'lucide-react';

const GoldChart = ({ history }) => {
    const safeHistory = Array.isArray(history) ? history : [];
    
    const chartData = useMemo(() => {
        return safeHistory.map(entry => {
            const date = new Date(entry.timestamp);
            return {
                gold: entry.total_gold / 10000, // Convert copper to gold
                time: date.getTime(),
                formattedDate: date.toLocaleDateString([], { day: '2-digit', month: '2-digit' }),
                fullDate: date.toLocaleString()
            };
        });
    }, [safeHistory]);

    const isUp = chartData.length > 1 && chartData[0].gold <= chartData[chartData.length - 1].gold;
    const currentGold = chartData.length > 0 ? chartData[chartData.length - 1].gold : 0;
    
    // Calculate difference if we have history
    let diff = 0;
    let percentDiff = 0;
    if (chartData.length > 1) {
        const startGold = chartData[0].gold;
        diff = currentGold - startGold;
        if (startGold > 0) {
            percentDiff = (diff / startGold) * 100;
        }
    }

    const formatGold = (value) => {
        if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
        if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
        return Math.floor(value).toString();
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-accent/30 transition-all duration-300">
            <div className="flex justify-between items-start mb-6 relative z-10">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider flex items-center gap-2">
                        <Landmark size={16} />
                        Account Reichtum
                    </h3>
                    <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-3xl font-bold text-white tracking-tight">{Math.floor(currentGold).toLocaleString()}</span>
                        <span className="text-accent text-sm font-medium">Gold</span>
                    </div>
                </div>
                
                {chartData.length > 1 && (
                    <div className="text-right">
                        <div className={`flex items-center gap-1 text-sm font-medium mb-1 justify-end ${isUp ? 'text-green-400' : 'text-red-400'}`}>
                            {isUp ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                            {isUp ? '+' : ''}{Math.floor(diff).toLocaleString()} g
                        </div>
                        <div className="text-secondary text-xs">
                            {isUp ? '+' : ''}{percentDiff.toFixed(2)}% (Gesamtzeitraum)
                        </div>
                    </div>
                )}
            </div>

            <div className="h-48 w-full mt-4">
                {chartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                            <defs>
                                <linearGradient id="goldGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#d4af37" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#d4af37" stopOpacity={0}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                            <XAxis 
                                dataKey="formattedDate" 
                                stroke="rgba(255,255,255,0.3)" 
                                fontSize={12} 
                                tickLine={false} 
                                axisLine={false}
                                minTickGap={20}
                            />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1a1a24', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                                itemStyle={{ color: '#d4af37', fontWeight: 'bold' }}
                                labelStyle={{ color: '#888' }}
                                formatter={(value) => [`${Math.floor(value).toLocaleString()} g`, "Gold"]}
                                labelFormatter={(label, payload) => {
                                    if (payload && payload.length > 0) {
                                        return payload[0].payload.fullDate;
                                    }
                                    return label;
                                }}
                            />
                            <Area 
                                type="monotone" 
                                dataKey="gold" 
                                stroke="#d4af37" 
                                strokeWidth={2}
                                fillOpacity={1} 
                                fill="url(#goldGradient)" 
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="h-full flex items-center justify-center text-secondary text-sm border-t border-white/5 pt-4">
                        Warte auf genügend Gold-Historie...
                    </div>
                )}
            </div>
        </div>
    );
};

export default GoldChart;
