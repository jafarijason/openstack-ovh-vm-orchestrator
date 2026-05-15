import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message = 'Loading...',
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const messageSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className={`${sizeClasses[size]} relative`}>
        <div
          className={`${sizeClasses[size]} border-4 border-gray-200 rounded-full`}
        ></div>
        <div
          className={`${sizeClasses[size]} absolute top-0 left-0 border-4 border-transparent border-t-blue-500 rounded-full animate-spin`}
        ></div>
      </div>
      <p className={`${messageSizeClasses[size]} text-gray-600`}>{message}</p>
    </div>
  );
};

export default LoadingSpinner;
