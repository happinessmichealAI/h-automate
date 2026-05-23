import React, { useState, useEffect } from 'react';

/**
 * LoadingState Component
 * Displays animated loading states for Business Insights and Smart Operations
 * 
 * Props:
 *   type: 'analysis' | 'operations' - determines which loading state to show
 *   duration: number - estimated duration in seconds (optional)
 */
const LoadingState = ({ type = 'analysis', duration = 15 }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showSlowMessage, setShowSlowMessage] = useState(false);

  // Loading steps for Business Insights
  const analysisSteps = [
    { label: 'Reading your file', icon: '📄', delay: 0 },
    { label: 'Understanding sales patterns', icon: '📊', delay: 2000 },
    { label: 'Identifying business risks', icon: '🔍', delay: 4000 },
    { label: 'Generating recommendations', icon: '💡', delay: 6000 },
    { label: 'Preparing your report', icon: '📝', delay: 8000 }
  ];

  // Loading steps for Smart Operations
  const operationsSteps = [
    { label: 'Analyzing your situation', icon: '🤔', delay: 0 },
    { label: 'Reviewing possible causes', icon: '🔎', delay: 3000 },
    { label: 'Building your action plan', icon: '📋', delay: 6000 }
  ];

  const steps = type === 'analysis' ? analysisSteps : operationsSteps;

  useEffect(() => {
    // Progress through steps
    const timers = steps.map((step, index) => {
      return setTimeout(() => {
        setCurrentStep(index);
      }, step.delay);
    });

    // Show slow network message after duration
    const slowTimer = setTimeout(() => {
      setShowSlowMessage(true);
    }, duration * 1000);

    return () => {
      timers.forEach(timer => clearTimeout(timer));
      clearTimeout(slowTimer);
    };
  }, [type, duration]);

  const handleTryAgain = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-[400px] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Main Loading Animation */}
        <div className="text-center mb-8">
          {/* Spinner */}
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-blue-600"></div>
          </div>

          {/* Header */}
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            {type === 'analysis' 
              ? 'Analyzing your business data...'
              : 'Understanding your business challenge...'}
          </h2>

          {/* Subtext */}
          <p className="text-gray-600">
            {type === 'analysis'
              ? "We're reviewing sales patterns, inventory trends, and business performance."
              : "We're identifying possible causes and practical next steps."}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-3 mb-6">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                index <= currentStep
                  ? 'bg-blue-50 border-2 border-blue-200'
                  : 'bg-gray-50 border-2 border-gray-200'
              }`}
            >
              {/* Icon */}
              <div className={`text-2xl transition-all duration-300 ${
                index < currentStep ? 'scale-100' : index === currentStep ? 'animate-pulse' : 'opacity-30'
              }`}>
                {index < currentStep ? '✓' : step.icon}
              </div>

              {/* Label */}
              <div className="flex-1">
                <p className={`font-medium transition-colors ${
                  index <= currentStep ? 'text-gray-900' : 'text-gray-400'
                }`}>
                  {step.label}
                </p>
              </div>

              {/* Status Indicator */}
              {index < currentStep && (
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              )}
              {index === currentStep && (
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              )}
            </div>
          ))}
        </div>

        {/* Time Estimate */}
        {!showSlowMessage && (
          <p className="text-center text-sm text-gray-500">
            This usually takes {duration}–{duration + 5} seconds.
          </p>
        )}

        {/* Slow Network Message */}
        {showSlowMessage && (
          <div className="mt-6 p-4 bg-amber-50 border-2 border-amber-200 rounded-xl">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⏳</span>
              <div className="flex-1">
                <h3 className="font-semibold text-amber-900 mb-1">
                  Still working on your analysis...
                </h3>
                <p className="text-sm text-amber-800 mb-3">
                  Complex business data may take a little longer.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={handleTryAgain}
                    className="px-4 py-2 bg-amber-600 text-white rounded-lg font-medium text-sm hover:bg-amber-700 transition-colors"
                  >
                    Try Again
                  </button>
                  <button
                    onClick={() => setShowSlowMessage(false)}
                    className="px-4 py-2 bg-white border-2 border-amber-600 text-amber-900 rounded-lg font-medium text-sm hover:bg-amber-50 transition-colors"
                  >
                    Keep Waiting
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${((currentStep + 1) / steps.length) * 100}%`
              }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingState;

// Made with Bob
