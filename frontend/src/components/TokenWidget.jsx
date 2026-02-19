import React from 'react';
import { TrendingUp, TrendingDown, Coins } from 'lucide-react';
import PriceChart from './PriceChart';

const TokenWidget = ({ formatted, history, selectedRange, onRangeChange }) => {
    const safeHistory = Array.isArray(history) ? history : [];
    const isUp = safeHistory.length > 1 && safeHistory[0].price <= safeHistory[safeHistory.length - 1].price;

    // Chart Data Preparation
    const chartData = safeHistory.map(entry => ({
        price: entry.price / 10000,
        time: entry.last_updated_timestamp,
        formattedTime: new Date(entry.last_updated_timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        formattedDate: new Date(entry.last_updated_timestamp * 1000).toLocaleDateString([], { day: '2-digit', month: '2-digit' })
    }));

    const ranges = [
        { label: '24H', value: '24h' },
        { label: '7D', value: '7d' },
        { label: '14D', value: '14d' },
        { label: '30D', value: '30d' }
    ];

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-accent/30 transition-all duration-300">
            <div className="flex justify-between items-start mb-4 relative z-10">
                <div>
                    <h3 className="text-secondary text-sm font-medium uppercase tracking-wider">WoW Token</h3>
                    <div className="flex items-baseline gap-2 mt-1">
                        <span className="text-3xl font-bold text-white tracking-tight">{formatted}</span>
                        <span className="text-accent text-sm font-medium">gold</span>
                    </div>
                </div>
                <div className={`p-2 rounded-lg ${isUp ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                    {isUp ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                </div>
            </div>

            {/* Range Selector */}
            <div className="flex gap-1 mb-4 relative z-10">
                {ranges.map(range => (
                    <button
                        key={range.value}
                        onClick={() => onRangeChange(range.value)}
                        className={`text-xs px-2 py-1 rounded transition-colors ${selectedRange === range.value
                            ? 'bg-accent/20 text-accent font-medium'
                            : 'text-secondary hover:text-white hover:bg-white/5'
                            }`}
                    >
                        {range.label}
                    </button>
                ))}
            </div>

            <div className="h-32 w-full opacity-75 group-hover:opacity-100 transition-opacity duration-500">
                <PriceChart
                    data={chartData}
                    selectedRange={selectedRange}
                    onRangeChange={onRangeChange}
                />
            </div>

            <div className="absolute top-0 right-0 p-3 opacity-10 pointer-events-none">
                <Coins size={100} />
            </div>
        </div>
    );
};

export default TokenWidget;
