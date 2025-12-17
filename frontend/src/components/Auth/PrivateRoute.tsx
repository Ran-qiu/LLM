import { ReactNode, useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuthStore } from '../../store/authStore'

interface PrivateRouteProps {
  children: ReactNode
}

export default function PrivateRoute({ children }: PrivateRouteProps) {
  const { isAuthenticated, isLoading, fetchCurrentUser } = useAuthStore()

  useEffect(() => {
    // Fetch current user if we have a token but no user data
    const token = localStorage.getItem('access_token')
    if (token && !isAuthenticated && !isLoading) {
      fetchCurrentUser()
    }
  }, [isAuthenticated, isLoading, fetchCurrentUser])

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
      }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
