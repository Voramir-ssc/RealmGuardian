import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import TokenWidget from './components/TokenWidget';
import GoldWidget from './components/GoldWidget';
import WatchlistWidget from './components/WatchlistWidget';

function App() {
  const [tokenData, setTokenData] = useState(null);
  const [tokenHistory, setTokenHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [range, setRange] = useState('24h');

  // Helper to ensure we use the same API URL logic
  const getApiUrl = () => import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const fetchTokenData = React.useCallback(async () => {
    try {
      let apiUrl = getApiUrl();
      let latestRes;
      try {
        latestRes = await fetch(`${apiUrl}/api/token/latest`);
      } catch {
        console.warn("Main API URL failed, trying localhost...");
        apiUrl = 'http://localhost:8000';
        latestRes = await fetch(`${apiUrl}/api/token/latest`);
      }

      const latest = await latestRes.json();

      const historyRes = await fetch(`${apiUrl}/api/token/history?range=${range}`);
      const history = await historyRes.json();

      setTokenData(latest);
      setTokenHistory(history);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch data", error);
      setError(error.message);
      setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchTokenData();
  }, [fetchTokenData]);

  useEffect(() => {
    const interval = setInterval(fetchTokenData, 60000);
    return () => clearInterval(interval);
  }, [fetchTokenData]);

  return (
    <Layout>
      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-xl mb-6">
          Error loading data: {error}. Check if Backend is running at {import.meta.env.VITE_API_URL || 'localhost:8000'}
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Token Card */}
        {loading ? (
          <div className="animate-pulse bg-surface h-48 rounded-2xl border border-white/5"></div>
        ) : (
          <TokenWidget
            currentPrice={tokenData?.price || 0}
            lastUpdated={tokenData?.last_updated || 0}
            formatted={tokenData?.formatted || "0g"}
            history={tokenHistory}
            selectedRange={range}
            onRangeChange={setRange}
          />
        )}

        {/* Account / Gold Card */}
        <GoldWidget apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:8000'} />

        <WatchlistWidget apiUrl={import.meta.env.VITE_API_URL || 'http://localhost:8000'} />
      </div>
    </Layout>
  );
}

export default App;
