import React, { useState, useEffect } from 'react';
import { Activity, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import PriceChart from './PriceChart';

const AnalyticsWidget = ({ apiUrl }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedItem, setExpandedItem] = useState(null);
    const [historyData, setHistoryData] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    useEffect(() => {
        fetchAnalytics();
    }, []);

    const fetchAnalytics = async () => {
        try {
            setLoading(true);
            const res = await fetch(`${apiUrl}/api/analysis/glyphs`);
            const data = await res.json();
            setItems(data);
        } catch (error) {
            console.error('Failed to fetch analytics:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchHistory = async (itemId) => {
        try {
            setHistoryLoading(true);
            const res = await fetch(`${apiUrl}/api/items/${itemId}/history?range=14d`);
            const data = await res.json();
            
            // Format for PriceChart
            const chartData = data.map(entry => ({
                price: entry.price / 10000, // convert copper to gold
                time: entry.last_updated_timestamp,
                formattedTime: new Date(entry.last_updated_timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                formattedDate: new Date(entry.last_updated_timestamp * 1000).toLocaleDateString([], { day: '2-digit', month: '2-digit' })
            }));
            
            setHistoryData(chartData);
        } catch (error) {
            console.error('Failed to fetch item history:', error);
        } finally {
            setHistoryLoading(false);
        }
    };

    const toggleExpand = (itemId) => {
        if (expandedItem === itemId) {
            setExpandedItem(null);
        } else {
            setExpandedItem(itemId);
            fetchHistory(itemId);
        }
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6 relative overflow-hidden flex flex-col h-full">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-accent/20 rounded-lg text-accent">
                        <Activity size={20} />
                    </div>
                    <h3 className="text-secondary font-medium tracking-wider">Top Liquidity Items</h3>
                </div>
                <button 
                    onClick={fetchAnalytics}
                    className="p-2 text-secondary hover:text-white transition-colors rounded-lg hover:bg-white/5"
                    disabled={loading}
                >
                    <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                </button>
            </div>

            {loading ? (
                <div className="flex-1 flex justify-center items-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
                </div>
            ) : items.length === 0 ? (
                <div className="flex-1 flex justify-center items-center text-secondary text-sm">
                    Keine profitablen Items gefunden.
                </div>
            ) : (
                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-3">
                    {items.map(item => (
                        <div key={item.item_id} className="bg-white/5 rounded-xl border border-white/5 overflow-hidden transition-all duration-300">
                            <div 
                                className="p-4 flex items-center justify-between cursor-pointer hover:bg-white/[0.07] transition-colors"
                                onClick={() => toggleExpand(item.item_id)}
                            >
                                <div className="flex-1">
                                    <div className="font-medium text-white">{item.name}</div>
                                    <div className="text-xs text-secondary mt-1 flex gap-3">
                                        <span>Ø {(item.sell_through_rate_24h).toFixed(1)}/Tag</span>
                                        <span>Score: {item.liquidity_score.toFixed(2)}</span>
                                    </div>
                                </div>
                                <div className="text-right mr-4">
                                    <div className="text-accent font-semibold">
                                        +{(item.profit / 10000).toFixed(0)}g
                                    </div>
                                    <div className="text-xs text-secondary mt-1">
                                        Preis: {(item.current_price / 10000).toFixed(0)}g
                                    </div>
                                </div>
                                <div className="text-secondary">
                                    {expandedItem === item.item_id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                                </div>
                            </div>
                            
                            {/* Expanded Graph Area */}
                            {expandedItem === item.item_id && (
                                <div className="p-4 border-t border-white/5 bg-black/20 h-48">
                                    {historyLoading ? (
                                        <div className="h-full flex justify-center items-center">
                                            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
                                        </div>
                                    ) : historyData.length > 0 ? (
                                        <PriceChart 
                                            data={historyData} 
                                            selectedRange="14d" 
                                            color="#a855f7" 
                                        />
                                    ) : (
                                        <div className="h-full flex justify-center items-center text-secondary text-xs">
                                            Keine Historie vorhanden
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AnalyticsWidget;
