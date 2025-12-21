import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import { Login, Register, PrivateRoute } from './components/Auth'
import { MainLayout } from './components/Common'
import ChatPage from './components/Chat/ChatPage'
import { APIKeyManagement } from './components/Models'
import { TagManagement } from './components/Tags'
import { ShareManagement } from './components/Shares'
import { TemplateManagement } from './components/Templates'
import { StatisticsPage } from './components/Statistics'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Private routes */}
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <MainLayout>
                  <ChatPage />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/api-keys"
            element={
              <PrivateRoute>
                <MainLayout>
                  <APIKeyManagement />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/tags"
            element={
              <PrivateRoute>
                <MainLayout>
                  <TagManagement />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/templates"
            element={
              <PrivateRoute>
                <MainLayout>
                  <TemplateManagement />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/shares"
            element={
              <PrivateRoute>
                <MainLayout>
                  <ShareManagement />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/statistics"
            element={
              <PrivateRoute>
                <MainLayout>
                  <StatisticsPage />
                </MainLayout>
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <MainLayout>
                  <Settings />
                </MainLayout>
              </PrivateRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </Router>
    </ConfigProvider>
  )
}

export default App
