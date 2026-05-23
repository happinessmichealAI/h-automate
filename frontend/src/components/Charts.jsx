import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * Charts Component
 * Displays maximum 3 charts: Revenue Trend, Top Products, Category Performance
 * 
 * Props:
 *   metrics: Metrics object from backend containing chart data
 */
const Charts = ({ metrics }) => {
  if (!metrics) return null;

  // Colors for charts
  const COLORS = {
    primary: '#1E40AF',
    secondary: '#14B8A6',
    accent: '#F59E0B',
    success: '#10B981',
    danger: '#EF4444',
    chart: ['#1E40AF', '#14B8A6', '#F59E0B', '#8B5CF6', '#EC4899']
  };

  // Parse monthly averages for revenue trend chart
  const getRevenueTrendData = () => {
    if (!metrics.monthly_averages?.value) return null;
    
    return Object.entries(metrics.monthly_averages.value).map(([month, data]) => ({
      month: month.substring(0, 3), // Shorten month name
      revenue: parseInt(data.daily_avg_revenue.replace(/[₦,]/g, ''))
    }));
  };

  // Parse top products for horizontal bar chart
  const getTopProductsData = () => {
    if (!metrics.top_products?.value) return null;
    
    return Object.entries(metrics.top_products.value)
      .slice(0, 5) // Maximum 5 products
      .map(([product, share]) => ({
        product: product.length > 15 ? product.substring(0, 15) + '...' : product,
        share: parseFloat(share.replace('%', ''))
      }))
      .reverse(); // Reverse for horizontal bar chart (highest at top)
  };

  // Parse category performance for donut chart
  const getCategoryData = () => {
    // Try different metric sources based on business type
    let categoryData = null;
    
    if (metrics.category_performance?.value) {
      categoryData = metrics.category_performance.value;
    } else if (metrics.transaction_types?.value) {
      // For POS agents
      categoryData = Object.entries(metrics.transaction_types.value).reduce((acc, [type, data]) => {
        acc[type] = data.share;
        return acc;
      }, {});
    } else if (metrics.top_products?.value) {
      // Fallback to top products
      categoryData = metrics.top_products.value;
    }
    
    if (!categoryData) return null;
    
    const entries = Object.entries(categoryData);
    
    // If more than 5 categories, group the rest as "Other"
    if (entries.length > 5) {
      const top5 = entries.slice(0, 5);
      const others = entries.slice(5);
      const othersTotal = others.reduce((sum, [, share]) => {
        return sum + parseFloat(share.replace('%', ''));
      }, 0);
      
      return [
        ...top5.map(([name, share]) => ({
          name,
          value: parseFloat(share.replace('%', ''))
        })),
        { name: 'Other', value: othersTotal }
      ];
    }
    
    return entries.map(([name, share]) => ({
      name,
      value: parseFloat(share.replace('%', ''))
    }));
  };

  const revenueTrendData = getRevenueTrendData();
  const topProductsData = getTopProductsData();
  const categoryData = getCategoryData();

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900">{label}</p>
          <p className="text-sm text-gray-600">
            {payload[0].name}: {payload[0].value}
            {payload[0].name.includes('revenue') ? '' : '%'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">Visual Insights</h2>
      
      {/* Chart 1: Revenue Trend (Line Chart) */}
      {revenueTrendData && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Revenue Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="month" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `₦${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke={COLORS.primary}
                strokeWidth={3}
                dot={{ fill: COLORS.primary, r: 5 }}
                activeDot={{ r: 7 }}
              />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-600 mt-2 text-center">
            Daily average revenue per month
          </p>
        </div>
      )}

      {/* Chart 2: Top Products (Horizontal Bar Chart) */}
      {topProductsData && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Top Products by Revenue
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={topProductsData} 
              layout="vertical"
              margin={{ left: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                type="number" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `${value}%`}
              />
              <YAxis 
                type="category" 
                dataKey="product" 
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
                width={100}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="share" 
                fill={COLORS.secondary}
                radius={[0, 8, 8, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
          <p className="text-sm text-gray-600 mt-2 text-center">
            Revenue share by product
          </p>
        </div>
      )}

      {/* Chart 3: Category Performance (Donut Chart) */}
      {categoryData && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Category Performance
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                labelLine={false}
              >
                {categoryData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={COLORS.chart[index % COLORS.chart.length]} 
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-4 mt-4">
            {categoryData.map((entry, index) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS.chart[index % COLORS.chart.length] }}
                />
                <span className="text-sm text-gray-700">{entry.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No charts available message */}
      {!revenueTrendData && !topProductsData && !categoryData && (
        <div className="bg-gray-50 rounded-2xl border border-gray-200 p-8 text-center">
          <p className="text-gray-600">
            Visual charts are not available for this analysis.
          </p>
        </div>
      )}
    </div>
  );
};

export default Charts;

// Made with Bob
