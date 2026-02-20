import React from 'react';
import { RefreshCw, Shield } from 'lucide-react';

const CharacterList = ({ characters, loading, onSync, onLogin }) => {
    const formatPlaytime = (seconds) => {
        if (!seconds) return "N/A";
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        return `${days}d ${hours}h`;
    };

    const getClassColor = (className) => {
        const colors = {
            'Death Knight': 'text-[#C41E3A]',
            'Demon Hunter': 'text-[#A330C9]',
            'Druid': 'text-[#FF7C0A]',
            'Evoker': 'text-[#33937F]',
            'Hunter': 'text-[#AAD372]',
            'Mage': 'text-[#3FC7EB]',
            'Monk': 'text-[#00FF98]',
            'Paladin': 'text-[#F48CBA]',
            'Priest': 'text-[#FFFFFF]',
            'Rogue': 'text-[#FFF468]',
            'Shaman': 'text-[#0070DE]',
            'Warlock': 'text-[#8788EE]',
            'Warrior': 'text-[#C69B6D]',
        };
        return colors[className] || 'text-white';
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-medium text-white">Your Characters</h3>
            </div>

            <div className="overflow-x-auto">
                {characters.length === 0 ? (
                    <div className="text-center py-12 text-secondary/50 border-2 border-dashed border-white/5 rounded-xl">
                        <p className="mb-4">No characters found.</p>
                        <button
                            onClick={onLogin}
                            className="bg-[#148eff] hover:bg-[#0074e0] text-white px-6 py-2.5 rounded-lg font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2 mx-auto"
                        >
                            <Shield size={18} />
                            Connect Battle.net
                        </button>
                    </div>
                ) : (
                    <table className="w-full text-left">
                        <thead>
                            <tr className="text-secondary text-xs border-b border-white/10">
                                <th className="pb-3 font-medium uppercase tracking-wider pl-4">Character</th>
                                <th className="pb-3 font-medium uppercase tracking-wider">Realm</th>
                                <th className="pb-3 font-medium uppercase tracking-wider">Level</th>
                                <th className="pb-3 font-medium uppercase tracking-wider">Playtime</th>
                                <th className="pb-3 font-medium uppercase tracking-wider text-right pr-4">Gold</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {characters.map((char) => (
                                <tr key={char.id} className="group hover:bg-white/5 transition-colors">
                                    <td className="py-3 pl-4">
                                        <div className="flex items-center gap-3">
                                            {char.icon_url ? (
                                                <img src={char.icon_url} alt="" className="w-8 h-8 rounded bg-black/40" />
                                            ) : (
                                                <div className="w-8 h-8 rounded bg-surface border border-white/10 flex items-center justify-center">
                                                    <span className="text-xs font-bold text-secondary">{char.name[0]}</span>
                                                </div>
                                            )}
                                            <div>
                                                <div className={`font-medium text-sm ${getClassColor(char.class_name)}`}>{char.name}</div>
                                                <div className="text-xs text-secondary/50">{char.class_name}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-3 text-sm text-secondary">{char.realm}</td>
                                    <td className="py-3 text-sm text-white">{char.level}</td>
                                    <td className="py-3 text-sm text-secondary font-mono">{formatPlaytime(char.played_time)}</td>
                                    <td className="py-3 text-sm font-bold text-white text-right pr-4">
                                        {(char.gold / 10000).toLocaleString('de-DE')} <span className="text-yellow-500 text-xs font-normal">g</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default CharacterList;
