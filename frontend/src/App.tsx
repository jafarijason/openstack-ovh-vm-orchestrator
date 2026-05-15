import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { VmList } from './pages/VmList';
import { VolumeList } from './pages/VolumeList';
import { SnapshotList } from './pages/SnapshotList';
import { ImageList } from './pages/ImageList';
import { Settings } from './pages/Settings';
import { NotFound } from './pages/NotFound';
import { useCloudStore } from './stores/cloudStore';

export const App: React.FC = () => {
  const { fetchCloudsStatus } = useCloudStore();

  useEffect(() => {
    // Fetch cloud status on app mount
    fetchCloudsStatus();
  }, [fetchCloudsStatus]);

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto">
            <div className="p-6">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/vms" element={<VmList />} />
                <Route path="/volumes" element={<VolumeList />} />
                <Route path="/snapshots" element={<SnapshotList />} />
                <Route path="/images" element={<ImageList />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
