import React from 'react';

/**
 * ErrorState Component
 * Displays user-friendly error messages with appropriate CTAs
 * 
 * Props:
 *   type: 'unreadable_file' | 'messy_data' | 'wrong_type' | 'ai_unavailable' | 'empty_state'
 *   message: Custom error message (optional)
 *   onRetry: Callback for retry action (optional)
 *   onViewSample: Callback for viewing sample format (optional)
 */
const ErrorState = ({ 
  type = 'ai_unavailable', 
  message = null,
  onRetry = null,
  onViewSample = null 
}) => {
  
  // Error configurations
  const errorConfigs = {
    unreadable_file: {
      icon: '📄',
      title: 'Could not read this file',
      message: message || "We couldn't understand this file format. Try CSV or Excel (.xlsx).",
      color: 'red',
      actions: [
        { label: 'View Sample File Format', onClick: onViewSample, variant: 'primary' },
        { label: 'Try Again', onClick: onRetry, variant: 'secondary' }
      ]
    },
    messy_data: {
      icon: '⚠️',
      title: 'Data quality issue',
      message: message || "Your file may be missing important sales information. We found inconsistent columns or missing values.",
      color: 'amber',
      actions: [
        { label: 'See How to Prepare Your File', onClick: onViewSample, variant: 'primary' },
        { label: 'Try Different File', onClick: onRetry, variant: 'secondary' }
      ]
    },
    wrong_type: {
      icon: '❌',
      title: 'Wrong file type',
      message: message || "This doesn't look like sales data. Upload a CSV or Excel sales file.",
      color: 'red',
      actions: [
        { label: 'Try Again', onClick: onRetry, variant: 'primary' }
      ]
    },
    ai_unavailable: {
      icon: '🔄',
      title: 'Analysis temporarily unavailable',
      message: message || "Analysis is taking longer than expected. Please try again shortly.",
      color: 'blue',
      actions: [
        { label: 'Try Again', onClick: onRetry, variant: 'primary' }
      ]
    },
    empty_state: {
      icon: '📊',
      title: 'No analysis yet',
      message: message || "Upload your sales file or try sample data to see what business insights look like.",
      color: 'gray',
      actions: [
        { label: 'See Sample Report', onClick: onViewSample, variant: 'primary' }
      ]
    }
  };

  const config = errorConfigs[type] || errorConfigs.ai_unavailable;

  // Color classes
  const colorClasses = {
    red: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-900',
      subtext: 'text-red-700',
      primary: 'bg-red-600 hover:bg-red-700 text-white',
      secondary: 'bg-white border-2 border-red-600 text-red-900 hover:bg-red-50'
    },
    amber: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-900',
      subtext: 'text-amber-700',
      primary: 'bg-amber-600 hover:bg-amber-700 text-white',
      secondary: 'bg-white border-2 border-amber-600 text-amber-900 hover:bg-amber-50'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-900',
      subtext: 'text-blue-700',
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-white border-2 border-blue-600 text-blue-900 hover:bg-blue-50'
    },
    gray: {
      bg: 'bg-gray-50',
      border: 'border-gray-200',
      text: 'text-gray-900',
      subtext: 'text-gray-700',
      primary: 'bg-blue-600 hover:bg-blue-700 text-white',
      secondary: 'bg-white border-2 border-gray-600 text-gray-900 hover:bg-gray-50'
    }
  };

  const colors = colorClasses[config.color];

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className={`${colors.bg} border-2 ${colors.border} rounded-2xl p-8 text-center`}>
          {/* Icon */}
          <div className="text-6xl mb-4">
            {config.icon}
          </div>

          {/* Title */}
          <h2 className={`text-2xl font-semibold ${colors.text} mb-3`}>
            {config.title}
          </h2>

          {/* Message */}
          <p className={`${colors.subtext} mb-6 leading-relaxed`}>
            {config.message}
          </p>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {config.actions.map((action, index) => (
              <button
                key={index}
                onClick={action.onClick}
                className={`px-6 py-3 rounded-xl font-medium transition-colors ${
                  action.variant === 'primary' 
                    ? colors.primary 
                    : colors.secondary
                }`}
              >
                {action.label}
              </button>
            ))}
          </div>

          {/* Additional help text for specific errors */}
          {type === 'messy_data' && (
            <div className="mt-6 pt-6 border-t border-amber-200">
              <p className="text-sm text-amber-800 mb-2 font-medium">
                Common issues:
              </p>
              <ul className="text-sm text-amber-700 text-left space-y-1">
                <li>• Missing date or product columns</li>
                <li>• Inconsistent date formats</li>
                <li>• Empty rows or merged cells</li>
                <li>• Revenue values with text characters</li>
              </ul>
            </div>
          )}

          {type === 'unreadable_file' && (
            <div className="mt-6 pt-6 border-t border-red-200">
              <p className="text-sm text-red-800">
                <strong>Supported formats:</strong> CSV (.csv) and Excel (.xlsx)
              </p>
            </div>
          )}
        </div>

        {/* Sample data preview for empty state */}
        {type === 'empty_state' && (
          <div className="mt-6 bg-white rounded-2xl border-2 border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">
              What you'll get:
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Business health scores across 4 key metrics</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>AI-powered insights you likely haven't noticed</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Specific, actionable recommendations</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Visual charts showing trends and patterns</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 font-bold">✓</span>
                <span>Downloadable PDF report</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorState;

// Made with Bob
