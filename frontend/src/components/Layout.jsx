import React from 'react';
import { LayoutDashboard, Coins, Settings } from 'lucide-react';

const Layout = ({ children, activeTab, onTabChange }) => {
    return (
        <div className="flex h-screen bg-background text-primary overflow-hidden">
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
                        label="Characters"
                        active={activeTab === 'characters'}
                        onClick={() => onTabChange('characters')}
                    />
                    <div className="flex-1" />
                    <NavItem
                        icon={<Settings size={20} />}
                        label="Settings"
                        active={activeTab === 'settings'}
                        onClick={() => onTabChange('settings')}
                    />
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden relative">
                {/* Header */}
                <header className="h-16 border-b border-white/5 flex items-center justify-between px-6 bg-surface/50 backdrop-blur-sm z-10">
                    <h1 className="text-xl font-medium text-white/90">Dashboard</h1>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/5">
                            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                            <span className="text-xs text-secondary font-mono">SYSTEM ONLINE</span>
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
