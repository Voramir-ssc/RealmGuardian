/**
 * CharacterList.jsx
 * 
 * Displays a formatted, scrollable grid of synced World of Warcraft characters.
 * Includes character-specific details such as realm, level, gold, and total playtime.
 */
import React, { useState } from 'react';
import { RefreshCw, Shield, ChevronDown, ChevronUp } from 'lucide-react';

const CharacterList = ({ characters, loading, onSync, onLogin }) => {
    const [expandedCharId, setExpandedCharId] = useState(null);

    const toggleExpand = (id) => {
        setExpandedCharId(expandedCharId === id ? null : id);
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

    const getItemQualityColor = (quality) => {
        const colors = {
            'POOR': 'text-[#9d9d9d]',
            'COMMON': 'text-[#ffffff]',
            'UNCOMMON': 'text-[#1eff00]',
            'RARE': 'text-[#0070dd]',
            'EPIC': 'text-[#a335ee]',
            'LEGENDARY': 'text-[#ff8000]',
            'ARTIFACT': 'text-[#e6cc80]'
        };
        return colors[quality] || 'text-gray-400';
    };

    return (
        <div className="bg-surface border border-white/5 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-medium text-white">Your Characters</h3>
            </div>

            <div className="overflow-x-auto">
                {loading && characters.length === 0 ? (
                    <div className="text-center py-12 border-2 border-dashed border-white/5 rounded-xl">
                        <RefreshCw size={32} className="animate-spin text-[#148eff] mx-auto mb-4" />
                        <p className="mb-2 text-white font-medium">Syncing characters from Battle.net...</p>
                        <p className="text-sm text-secondary/50">This may take a few seconds.</p>
                    </div>
                ) : characters.length === 0 ? (
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
                                <th className="pb-3 w-8"></th>
                                <th className="pb-3 font-medium uppercase tracking-wider pl-4">Character</th>
                                <th className="pb-3 font-medium uppercase tracking-wider">Realm</th>
                                <th className="pb-3 font-medium uppercase tracking-wider text-center">Level</th>
                                <th className="pb-3 font-medium uppercase tracking-wider text-center text-[#ff8000]">iLvl</th>
                                <th className="pb-3 font-medium uppercase tracking-wider text-right pr-4">Gold</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {characters.map((char) => {
                                let equipment = [];
                                try {
                                    if (char.equipment) {
                                        equipment = JSON.parse(char.equipment);
                                    }
                                } catch (e) {
                                    console.error("Failed to parse equipment JSON", e);
                                }
                                const isExpanded = expandedCharId === char.id;

                                return (
                                    <React.Fragment key={char.id}>
                                        <tr
                                            className="group hover:bg-white/5 transition-colors cursor-pointer"
                                            onClick={() => toggleExpand(char.id)}
                                        >
                                            <td className="py-3 text-secondary/50 pl-2">
                                                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                            </td>
                                            <td className="py-3 pl-2">
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
                                            <td className="py-3 text-sm text-white text-center font-medium">{char.level}</td>
                                            <td className="py-3 text-sm font-bold text-[#ff8000] text-center">{char.item_level || '-'}</td>
                                            <td className="py-3 text-sm font-bold text-white text-right pr-4">
                                                {(char.gold / 10000).toLocaleString('de-DE')} <span className="text-yellow-500 text-xs font-normal">g</span>
                                            </td>
                                        </tr>

                                        {/* Dropdown Row */}
                                        {isExpanded && (
                                            <tr className="bg-black/20">
                                                <td colSpan="6" className="py-4 px-6 border-l-4 border-[#148eff]/50">

                                                    {/* Professions Section */}
                                                    <div className="mb-4">
                                                        <div className="mb-2 text-xs uppercase tracking-wider text-secondary font-medium">Professions</div>
                                                        {professions.length > 0 ? (
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                                {professions.map((prof, idx) => {
                                                                    const percentage = prof.max_skill_points ? Math.min(100, (prof.skill_points / prof.max_skill_points) * 100) : 0;
                                                                    return (
                                                                        <div key={idx} className="p-3 rounded-lg bg-surface border border-white/5 flex flex-col gap-2">
                                                                            <div className="flex justify-between items-center text-sm font-medium text-white">
                                                                                <span>{prof.name}</span>
                                                                                <span className="text-secondary/80 text-xs">{prof.skill_points} / {prof.max_skill_points}</span>
                                                                            </div>
                                                                            <div className="w-full bg-black/40 h-1.5 rounded-full overflow-hidden">
                                                                                <div
                                                                                    className="bg-[#148eff] h-full rounded-full transition-all duration-1000"
                                                                                    style={{ width: `${percentage}%` }}
                                                                                />
                                                                            </div>
                                                                        </div>
                                                                    );
                                                                })}
                                                            </div>
                                                        ) : (
                                                            <div className="text-sm text-secondary/50 italic py-2">
                                                                No professions data synced.
                                                            </div>
                                                        )}
                                                    </div>

                                                    {/* Equipment Section */}
                                                    <div>
                                                        <div className="mb-2 text-xs uppercase tracking-wider text-secondary font-medium">Equipped Items ({equipment.length})</div>
                                                        {equipment.length > 0 ? (
                                                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                                                {equipment.map((item, idx) => (
                                                                    <div key={idx} className="flex justify-between items-center text-xs p-2 rounded bg-surface border border-white/5 hover:border-white/10 transition-colors">
                                                                        <div className="flex flex-col truncate pr-2">
                                                                            <span className={`font-medium ${getItemQualityColor(item.quality)} truncate`}>{item.name}</span>
                                                                            <span className="text-secondary/50 text-[10px] uppercase">
                                                                                {item.slot ? item.slot.replace(/_/g, ' ') : 'Unknown Slot'}
                                                                            </span>
                                                                        </div>
                                                                        <span className="text-[#ff8000] font-bold shrink-0">{item.level}</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="text-sm text-secondary/50 italic py-2">
                                                                No equipment data synced or character is hidden.
                                                            </div>
                                                        )}
                                                    </div>

                                                </td>
                                            </tr>
                                        )}
                                    </React.Fragment>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default CharacterList;
