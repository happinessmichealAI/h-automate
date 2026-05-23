import React from 'react';

/**
 * HealthSnapshot Component
 * Displays 4 color-coded business health metrics
 * 
 * Props:
 *   metrics: Object containing health scores from diagnosis
 */
const HealthSnapshot = ({ metrics }) => {
  // Parse health snapshot from diagnosis text
  const parseHealthMetrics = (diagnosisText) => {
    if (!diagnosisText) return null;
    
    const healthSection = diagnosisText.split('---')[0];
    if (!healthSection.includes('BUSINESS HEALTH SNAPSHOT')) return null;
    
    const lines = healthSection.split('\n').filter(line => line.trim());
    const scores = {};
    
    lines.forEach(line => {
      // Match pattern: "Metric Name: XX/100 — Status"
      const match = line.match(/(.+?):\s*(\d+)\/100\s*—\s*(.+)/);
      if (match) {
        const [, name, score, status] = match;
        scores[name.trim()] = {
          score: parseInt(score),
          status: status.trim()
        };
      }
    });
    
    return scores;
  };
  
  const healthMetrics = parseHealthMetrics(metrics);
  
  if (!healthMetrics) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Business Health Snapshot
        </h2>
        <p className="text-gray-600">Health metrics not available</p>
      </div>
    );
  }
  
  // Get color based on score
  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 50) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };
  
  const getScoreIcon = (score) => {
    if (score >= 75) return '✅';
    if (score >= 50) return '🟡';
    return '🔴';
  };
  
  // Main metrics to display (first 4)
  const mainMetrics = Object.entries(healthMetrics)
    .filter(([name]) => !name.includes('Overall'))
    .slice(0, 4);
  
  // Overall health (if available)
  const overallHealth = Object.entries(healthMetrics)
    .find(([name]) => name.includes('Overall'));
  
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">
        Business Health Snapshot
      </h2>
      
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {mainMetrics.map(([name, data]) => (
          <div
            key={name}
            className={`p-4 rounded-xl border-2 transition-all hover:shadow-md ${getScoreColor(data.score)}`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold text-sm">{name}</h3>
              <span className="text-xl">{getScoreIcon(data.score)}</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{data.score}</span>
              <span className="text-lg text-gray-600">/100</span>
            </div>
            <p className="text-sm font-medium mt-1">{data.status}</p>
          </div>
        ))}
      </div>
      
      {/* Overall Health (if available) */}
      {overallHealth && (
        <div className={`p-5 rounded-xl border-2 ${getScoreColor(overallHealth[1].score)}`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg mb-1">{overallHealth[0]}</h3>
              <p className="text-sm font-medium">{overallHealth[1].status}</p>
            </div>
            <div className="text-right">
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold">{overallHealth[1].score}</span>
                <span className="text-xl text-gray-600">/100</span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Top Risk (if available in diagnosis) */}
      {metrics && metrics.includes('Top Risk:') && (
        <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
          <h4 className="font-semibold text-red-900 mb-1 flex items-center gap-2">
            <span>⚠️</span>
            Top Risk
          </h4>
          <p className="text-red-800 text-sm">
            {metrics.split('Top Risk:')[1]?.split('\n')[0]?.trim()}
          </p>
        </div>
      )}
    </div>
  );
};

export default HealthSnapshot;

// Made with Bob
