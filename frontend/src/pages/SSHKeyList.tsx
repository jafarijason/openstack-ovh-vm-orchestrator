import React, { useEffect, useState } from 'react';
import { sshKeyService } from '../services/sshKeyService';
import { useCloudStore } from '../stores/cloudStore';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorAlert } from '../components/common/ErrorAlert';
import { MetadataViewer } from '../components/common/MetadataViewer';
import type { components } from '../types/api';

type SSHKeyResponse = components['schemas']['SSHKeyResponse'];

export const SSHKeyList: React.FC = () => {
  const { activeCloud, activeClouds } = useCloudStore();
  const [sshKeys, setSSHKeys] = useState<SSHKeyResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedKeyName, setExpandedKeyName] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const loadSSHKeys = async (cloud: string) => {
    try {
      setLoading(true);
      setSSHKeys([]);
      const response = await sshKeyService.listSSHKeys(100, 0, cloud);
      setSSHKeys(response.data);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load SSH keys';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load SSH keys when activeCloud changes
    if (activeCloud && activeCloud.trim()) {
      loadSSHKeys(activeCloud);
    }
  }, [activeCloud]);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const truncateKey = (key: string, length = 60): string => {
    if (key.length <= length) return key;
    return key.substring(0, length) + '...';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">SSH Keys</h1>
        <p className="text-gray-600 mt-1">
          {sshKeys.length} SSH key{sshKeys.length !== 1 ? 's' : ''} available
        </p>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}

      {loading ? (
        <div className="flex justify-center py-12">
          <LoadingSpinner message="Loading SSH keys..." />
        </div>
      ) : sshKeys.length === 0 ? (
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
              d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
            />
          </svg>
          <p className="text-gray-600 text-lg">No SSH keys found</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="w-8 px-4 py-3"></th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Fingerprint
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Comment
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {sshKeys.map((key) => (
                  <React.Fragment key={key.name}>
                    <tr
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => setExpandedKeyName(expandedKeyName === key.name ? null : key.name)}
                    >
                      <td className="px-4 py-4 text-center">
                        <span className="text-gray-400">
                          {expandedKeyName === key.name ? '▼' : '▶'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {key.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          {key.type || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                        <span title={key.fingerprint || ''}>
                          {key.fingerprint ? truncateKey(key.fingerprint, 40) : '-'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {key.comment || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {key.created_at
                          ? new Date(key.created_at).toLocaleDateString()
                          : '-'}
                      </td>
                    </tr>
                    {expandedKeyName === key.name && (
                      <>
                        <tr className="bg-gray-100 border-b border-gray-200">
                          <td colSpan={6} className="px-6 py-4">
                            <div className="space-y-4">
                              {/* Public Key Section */}
                              <div>
                                <div className="flex justify-between items-center mb-2">
                                  <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">
                                    Public Key
                                  </h4>
                                  <button
                                    onClick={() => copyToClipboard(key.public_key, key.name)}
                                    className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                                  >
                                    {copiedKey === key.name ? '✓ Copied' : 'Copy'}
                                  </button>
                                </div>
                                <div className="bg-gray-900 rounded p-3 overflow-x-auto">
                                  <code className="text-xs text-green-400 font-mono break-all">
                                    {key.public_key}
                                  </code>
                                </div>
                              </div>

                              {/* Key Details */}
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                    Fingerprint
                                  </h4>
                                  <p className="text-sm font-mono text-gray-900 break-all">
                                    {key.fingerprint || '-'}
                                  </p>
                                </div>
                                <div>
                                  <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                                    Type
                                  </h4>
                                  <p className="text-sm text-gray-900">{key.type || '-'}</p>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                        <tr className="bg-gray-50">
                          <td colSpan={6} className="px-6 py-4">
                            <MetadataViewer
                              metadata={key.metadata}
                              name={`Metadata - ${key.name}`}
                            />
                          </td>
                        </tr>
                      </>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SSHKeyList;
