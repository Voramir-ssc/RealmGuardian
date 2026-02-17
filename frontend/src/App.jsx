import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import TokenWidget from './components/TokenWidget';

function App() {
  const [tokenData, setTokenData] = useState(null);
  const [tokenHistory, setTokenHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTokenData = async () => {
    try {
      const latestRes = await fetch('http://localhost:8000/api/token/latest');
      const latest = await latestRes.json();

      const historyRes = await fetch('http://localhost:8000/api/token/history?limit=24');
      const history = await historyRes.json();

      setTokenData(latest);
      setTokenHistory(history);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch data", error);
    }
  };

  useEffect(() => {
    fetchTokenData();
    const interval = setInterval(fetchTokenData, 60000); // Poll every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <Layout>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Token Card */}
        {loading ? (
          <div className="animate-pulse bg-surface h-48 rounded-2xl border border-white/5"></div>
        ) : (
          <TokenWidget currentPrice={tokenData?.price || 0} history={tokenHistory} />
        )}

        {/* Placeholder for Watchlist */}
        <div className="bg-surface border border-white/5 rounded-2xl p-6 md:col-span-2">
          <h3 className="text-secondary text-sm font-medium uppercase tracking-wider mb-4">Market Watchlist</h3>
          <div className="flex flex-col items-center justify-center h-32 text-secondary/50 border-2 border-dashed border-white/5 rounded-xl">
            <span>No items tracked yet</span>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default App;
