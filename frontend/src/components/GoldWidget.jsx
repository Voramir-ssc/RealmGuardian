import React, { useState, useEffect } from 'react';
import { Coins, User, LogIn, ExternalLink, RefreshCw } from 'lucide-react';

const GoldWidget = ({ apiUrl }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Try fetch
            let url = apiUrl || 'http://localhost:8000';
            const res = await fetch(`${url}/api/user/characters`);
            if (res.ok) {
                const json = await res.json();
                setData(json);
            } else {
                // misuse 404/500 to mean "not connected" or just empty
                setData(null);
            }
        } catch (e) {
            console.error("Failed to fetch characters", e);
            setData(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();

        // Check for connected param to trigger immediate refresh
        const params = new URLSearchParams(window.location.search);
        if (params.get('connected')) {
            // Clean URL
            window.history.replaceState({}, document.title, "/");
            fetchData();
        }
    }, []);

    const handleLogin = () => {
        window.location.href = `${apiUrl}/api/auth/login`;
    };

    const formatGold = (copper) => {
        return (copper / 10000).toLocaleString('de-DE');
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-secondary text-sm font-medium uppercase tracking-wider">Battle.net Account</h3>
                {data && (
                    <button onClick={fetchData} disabled={loading} className="text-secondary/50 hover:text-white transition-colors">
                        <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                    </button>
                )}
            </div>

            {!data || data.characters.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="w-12 h-12 bg-[#148eff]/20 rounded-full flex items-center justify-center mb-4 text-[#148eff]">
                        <User size={24} />
                    </div>
                    <div className="text-white font-medium mb-2">Connect Battle.net</div>
                    <p className="text-secondary/50 text-xs mb-6 max-w-[200px]">
                        Import your characters to see your total gold wealth across your account.
                    </p>
                    <button
                        onClick={handleLogin}
                        className="bg-[#148eff] hover:bg-[#148eff]/80 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                    >
                        <LogIn size={16} />
                        Connect
                    </button>
                </div>
            ) : (
                <div>
                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-12 h-12 rounded-full bg-yellow-500/20 flex items-center justify-center text-yellow-500 border border-yellow-500/20">
                            <Coins size={24} />
                        </div>
                        <div>
                            <div className="text-secondary text-xs uppercase tracking-wider">Total Wealth</div>
                            <div className="text-2xl font-bold text-white tracking-tight">
                                {formatGold(data.total_gold)}<span className="text-yellow-500 ml-0.5">g</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                        {data.characters.map((char) => (
                            <div key={char.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors group">
                                <div className="flex items-center gap-3">
                                    {char.icon_url ? (
                                        <img src={char.icon_url} alt="" className="w-8 h-8 rounded bg-black/50" />
                                    ) : (
                                        <div className="w-8 h-8 rounded bg-white/10 flex items-center justify-center text-xs font-bold text-secondary">
                                            {char.level}
                                        </div>
                                    )}
                                    <div>
                                        <div className="text-white text-sm font-medium leading-none mb-1">{char.name}</div>
                                        <div className="text-secondary/50 text-[10px] flex gap-2">
                                            <span>{char.realm}</span>
                                            <span>•</span>
                                            <span className="text-white/60">{char.class_name}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-white text-sm font-medium">
                                        {formatGold(char.gold)}<span className="text-yellow-500/50 text-xs ml-0.5">g</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default GoldWidget;
