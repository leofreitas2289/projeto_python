import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  // Configurar axios com o token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Verificar se o token ainda é válido
      fetchUserProfile()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('/api/users/me/')
      setUser(response.data)
    } catch (error) {
      console.error('Erro ao buscar perfil do usuário:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post('/api/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      await fetchUserProfile()
      return { success: true }
    } catch (error) {
      console.error('Erro no login:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Erro ao fazer login' 
      }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/api/users/', {
        username,
        email,
        password
      })
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Erro no registro:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Erro ao criar conta' 
      }
    }
  }

  const value = {
    user,
    token,
    login,
    logout,
    register,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

