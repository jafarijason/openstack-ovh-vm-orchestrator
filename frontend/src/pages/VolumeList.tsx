import React from 'react';

export const VolumeList: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Volumes</h1>
        <p className="text-gray-600 mt-1">Manage persistent block storage volumes</p>
      </div>

      <div className="bg-white rounded-lg shadow p-12 text-center">
        <svg
          className="w-16 h-16 text-gray-400 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M5 12h14M5 12a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v5a2 2 0 01-2 2M5 12a2 2 0 00-2 2v5a2 2 0 002 2h14a2 2 0 002-2v-5a2 2 0 00-2-2m-2-4H7a2 2 0 00-2 2v4a2 2 0 002 2h10a2 2 0 002-2V8a2 2 0 00-2-2z"
          />
        </svg>
        <p className="text-gray-600 text-lg">Volume management coming soon</p>
        <p className="text-gray-500 text-sm mt-1">
          Create, manage, and attach volumes to your VMs
        </p>
      </div>
    </div>
  );
};

export default VolumeList;
