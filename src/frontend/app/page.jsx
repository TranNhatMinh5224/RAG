'use client';

import React, { useContext, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthContext } from '../src/contexts/AuthContext';
import DashboardPage from '../src/views/DashboardPage';

export default function Home() {
  const { user, loading } = useContext(AuthContext);
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div 
        style={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          background: 'var(--bg-app-base)',
          color: 'var(--text-secondary)'
        }}
      >
        <div className="text-center">
          <div className="spinner-border text-info mb-3" role="status" />
          <div>Đang kết nối hệ thống RAG Enterprise...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <DashboardPage />;
}
