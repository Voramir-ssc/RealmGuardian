import React from 'react';
import { AreaChart, Area, ResponsiveContainer, YAxis } from 'recharts';
import { TrendingUp, TrendingDown, Coins } from 'lucide-react';

const TokenWidget = ({ currentPrice, history }) => {
    const isUp = history.length > 1 && history[0].price >= history[history.length - 1].price;
    const formattedPrice = (currentPrice / 10000).toLocaleString('de-DE');

    // Prepare data for chart (reverse if history is descending time)
    const chartData = [...history].reverse().map(entry => ({
        price: entry.price / 10000,
        time: new Date(entry.last_updated_timestamp * 1000).toLocaleTimeString()
    }));

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-accent/30 transition-all duration-300">
            <div className="flex justify-between items-start mb-4 relative z-10">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider">WoW Token</h3>
                    <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-3xl font-bold text-white tracking-tight">{formattedPrice}</span>
                        <span className="text-accent text-sm font-medium">gold</span>
                    </div>
                </div>
                <div className={`p-2 rounded-lg ${isUp ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                    {isUp ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                </div>
            </div>

            <div className="h-16 w-full opacity-50 group-hover:opacity-100 transition-opacity duration-500">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#00ced1" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#00ced1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <YAxis domain={['dataMin', 'dataMax']} hide />
                        <Area
                            type="monotone"
                            dataKey="price"
                            stroke="#00ced1"
                            fillOpacity={1}
                            fill="url(#colorPrice)"
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            <div className="absolute top-0 right-0 p-3 opacity-10">
                <Coins size={100} />
            </div>
        </div>
    );
};

export default TokenWidget;
