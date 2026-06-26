/**
 * Layout.jsx
 * 
 * Main layout wrapper for the RealmGuardian application.
 * Provides the sidebar navigation structure and content area container.
 */
import React from 'react';
import { LayoutDashboard, Coins, Settings, Hammer } from 'lucide-react';

const Layout = ({ children, activeTab, onTabChange, theme = 'dark', setTheme = () => {} }) => {
    const getTabTitle = (tab) => {
        switch (tab) {
            case 'dashboard': return 'Dashboard';
            case 'characters': return 'Charaktere';
            case 'crafting': return 'Handwerk';
            case 'settings': return 'Einstellungen';
            default: return 'Dashboard';
        }
    };

    const themeClass = theme === 'dark' ? '' : `theme-${theme}`;

    return (
        <div className={`flex h-screen bg-background text-primary overflow-hidden theme-transition ${themeClass}`}>
            {/* Sidebar */}
            <aside className="w-16 md:w-64 bg-surface border-r border-white/5 flex flex-col transition-all duration-300">
                <div className="p-4 flex items-center justify-center md:justify-start gap-3 border-b border-white/5 h-16">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-purple-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,206,209,0.3)]">
                        <span className="font-bold text-white text-xs">RG</span>
                    </div>
                    <span className="font-bold text-lg hidden md:block tracking-wide">RealmGuardian</span>
                </div>

                <nav className="flex-1 p-2 gap-1 flex flex-col mt-4">
                    <NavItem
                        icon={<LayoutDashboard size={20} />}
                        label="Dashboard"
                        active={activeTab === 'dashboard'}
                        onClick={() => onTabChange('dashboard')}
                    />
                    <NavItem
                        icon={<Coins size={20} />}
                        label="Charaktere"
                        active={activeTab === 'characters'}
                        onClick={() => onTabChange('characters')}
                    />
                    <NavItem
                        icon={<Hammer size={20} />}
                        label="Handwerk"
                        active={activeTab === 'crafting'}
                        onClick={() => onTabChange('crafting')}
                    />
                    <div className="flex-1" />
                    <NavItem
                        icon={<Settings size={20} />}
                        label="Einstellungen"
                        active={activeTab === 'settings'}
                        onClick={() => onTabChange('settings')}
                    />
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden relative">
                {/* Header */}
                <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-surface/50 backdrop-blur-sm z-10">
                    <h1 className="text-xl font-medium text-white/90">{getTabTitle(activeTab)}</h1>
                    <div className="flex items-center gap-4">
                        {/* Theme Quick Selector */}
                        <div className="flex items-center gap-2 mr-2 bg-black/20 rounded-full px-3 py-1.5 border border-white/5">
                            <span className="text-[10px] text-secondary font-semibold uppercase tracking-wider mr-1 hidden sm:inline">Design:</span>
                            {[
                                { id: 'dark', color: 'bg-cyan-400', label: 'Standard Dark' },
                                { id: 'druid', color: 'bg-orange-500', label: 'Druide (Lenmera)' },
                                { id: 'horde', color: 'bg-red-600', label: 'Horde' },
                                { id: 'alliance', color: 'bg-yellow-500', label: 'Allianz' }
                            ].map((t) => (
                                <button
                                    key={t.id}
                                    onClick={() => setTheme(t.id)}
                                    title={t.label}
                                    className={`w-3.5 h-3.5 rounded-full transition-all duration-300 ${t.color} cursor-pointer relative hover:scale-125 ${
                                        theme === t.id 
                                            ? 'ring-2 ring-white ring-offset-2 ring-offset-black scale-110 shadow-[0_0_10px_rgba(255,255,255,0.4)]' 
                                            : 'opacity-60 hover:opacity-100'
                                    }`}
                                />
                            ))}
                        </div>

                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/5">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                            <span className="text-xs text-secondary font-mono">SYSTEM BEREIT</span>
                        </div>
                    </div>
                </header>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto p-6 relative">
                    {/* Background Grid Effect */}
                    <div className="absolute inset-0 z-0 opacity-[0.02]"
                        style={{ backgroundImage: 'linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
                    </div>

                    <div className="relative z-10 max-w-7xl mx-auto space-y-6">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
};

const NavItem = ({ icon, label, active = false, onClick }) => (
    <button
        onClick={onClick}
        className={`
    w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group
    ${active
                ? 'bg-accent/10 text-accent border border-accent/20'
                : 'text-secondary hover:bg-white/5 hover:text-white'}
  `}>
        <div className={`${active ? 'text-accent' : 'text-secondary group-hover:text-white'}`}>
            {icon}
        </div>
        <span className="hidden md:block text-sm font-medium">{label}</span>
        {active && <div className="ml-auto w-1 h-1 rounded-full bg-accent md:block hidden shadow-[0_0_8px_currentColor]" />}
    </button>
);

export default Layout;
