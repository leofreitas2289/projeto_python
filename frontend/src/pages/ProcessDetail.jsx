import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  ArrowLeft, 
  Calendar, 
  User, 
  FileText, 
  Brain, 
  Tag, 
  MapPin, 
  Building, 
  DollarSign,
  Clock,
  AlertCircle,
  CheckCircle,
  Pencil
} from 'lucide-react'
import axios from 'axios'

const ProcessDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  
  const [process, setProcess] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState('')
  const [editedDescription, setEditedDescription] = useState('')
  const handleSaveEdit = async () => {
    try {
      const response = await axios.put(`/api/processes/${id}`, {
        title: editedTitle,
        description: editedDescription,
      });
      setProcess(response.data);
      setIsEditing(false);
      alert("Processo atualizado com sucesso!");
    } catch (error) {
      console.error("Erro ao salvar processo:", error);
      alert("Erro ao salvar processo. Tente novamente.");
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedTitle(process.title);
    setEditedDescription(process.description);
  };

  useEffect(() => {
    fetchProcess();
  }, [id]);

  useEffect(() => {
    if (process) {
      setEditedTitle(process.title);
      setEditedDescription(process.description);
    }
  }, [process]);

  const fetchProcess = async () => {
    console.log('Fetching process with ID:', id)
    try {
      const response = await axios.get(`/api/processes/${id}`)
      console.log('Process fetched successfully:', response.data)
      setProcess(response.data)
    } catch (error) {
      console.error('Erro ao buscar processo:', error)
      console.error('Error response:', error.response)
      if (error.response?.status === 404) {
        navigate('/dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  const analyzeProcess = async () => {
    console.log('Analyzing process with ID:', id)
    setAnalyzing(true)
    try {
      const response = await axios.post(`/api/processes/${id}/analyze`)
      console.log('Analysis completed successfully:', response.data)
      setAnalysis(response.data)
    } catch (error) {
      console.error('Erro ao analisar processo:', error)
      console.error('Error response:', error.response)
      alert('Erro ao analisar processo. Tente novamente.')
    } finally {
      setAnalyzing(false)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getEntityIcon = (type) => {
    switch (type) {
      case 'PER':
        return <User className="h-4 w-4" />
      case 'ORG':
        return <Building className="h-4 w-4" />
      case 'LOC':
        return <MapPin className="h-4 w-4" />
      default:
        return <Tag className="h-4 w-4" />
    }
  }

  const getEntityColor = (type) => {
    switch (type) {
      case 'PER':
        return 'bg-blue-100 text-blue-800'
      case 'ORG':
        return 'bg-green-100 text-green-800'
      case 'LOC':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getSuggestionIcon = (type) => {
    switch (type) {
      case 'CAMPO_PADRONIZADO':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'DATA_REFERENCIA':
        return <Calendar className="h-4 w-4 text-blue-500" />
      case 'VALOR_ENVOLVIDO':
        return <DollarSign className="h-4 w-4 text-yellow-500" />
      case 'PALAVRA_CHAVE':
        return <AlertCircle className="h-4 w-4 text-orange-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-gray-500" />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!process) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900">Processo não encontrado</h2>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Voltar ao Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-5 w-5" />
                <span>Voltar</span>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{process.title}</h1>
                <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Criado em {formatDate(process.created_at)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <User className="h-4 w-4" />
                    <span>{user?.username}</span>
                  </div>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsEditing(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <Pencil className="h-4 w-4" />
              <span>Editar Processo</span>
            </button>
            <button
              onClick={analyzeProcess}
              disabled={analyzing}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
            >
              <Brain className="h-4 w-4" />
              <span>{analyzing ? 'Analisando...' : 'Analisar Processo'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Process Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-2 mb-4">
                <FileText className="h-5 w-5 text-gray-400" />
                <h2 className="text-lg font-semibold text-gray-900">Detalhes do Processo</h2>
              </div>
              
              <div className="space-y-4">
                {isEditing ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Título
                      </label>
                      <input
                        type="text"
                        value={editedTitle}
                        onChange={(e) => setEditedTitle(e.target.value)}
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Descrição
                      </label>
                      <textarea
                        value={editedDescription}
                        onChange={(e) => setEditedDescription(e.target.value)}
                        rows="5"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      ></textarea>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={handleSaveEdit}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                      >
                        Salvar
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="px-4 py-2 bg-gray-300 text-gray-800 rounded-md hover:bg-gray-400"
                      >
                        Cancelar
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Título
                      </label>
                      <p className="text-gray-900">{process.title}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Descrição
                      </label>
                      <div className="bg-gray-50 rounded-md p-4">
                        <p className="text-gray-900 whitespace-pre-wrap">
                          {process.description || 'Sem descrição'}
                        </p>
                      </div>
                    </div>
                  </>
                )}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Criado em
                    </label>
                    <p className="text-gray-900">{formatDate(process.created_at)}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Atualizado em
                    </label>
                    <p className="text-gray-900">{formatDate(process.updated_at)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Analysis Results */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Brain className="h-5 w-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Análise de NLP</h2>
              </div>
              
              {!analysis ? (
                <div className="text-center py-8">
                  <Brain className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-sm font-medium text-gray-900 mb-2">
                    Análise não realizada
                  </h3>
                  <p className="text-sm text-gray-500 mb-4">
                    Clique em "Analisar Processo" para extrair entidades e gerar sugestões.
                  </p>
                  <button
                    onClick={analyzeProcess}
                    disabled={analyzing}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                  >
                    <Brain className="h-4 w-4 mr-2" />
                    {analyzing ? 'Analisando...' : 'Analisar Agora'}
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Entidades Nomeadas */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">
                      Entidades Identificadas
                    </h3>
                    {analysis.entidades_nomeadas?.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {analysis.entidades_nomeadas.map((entity, index) => (
                          <span
                            key={index}
                            className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${getEntityColor(entity.tipo_entidade)}`}
                          >
                            {getEntityIcon(entity.tipo_entidade)}
                            <span>{entity.texto}</span>
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">Nenhuma entidade identificada</p>
                    )}
                  </div>

                  {/* Sugestões do Agente */}
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">
                      Sugestões de Padronização
                    </h3>
                    {analysis.sugestoes_do_agente?.length > 0 ? (
                      <div className="space-y-3">
                        {analysis.sugestoes_do_agente.map((suggestion, index) => (
                          <div
                            key={index}
                            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                          >
                            <div className="flex items-start space-x-3">
                              {getSuggestionIcon(suggestion.tipo_sugestao)}
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900 mb-1">
                                  {suggestion.descricao}
                                </p>
                                <p className="text-xs text-gray-600">
                                  {suggestion.acao_recomendada}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500">Nenhuma sugestão gerada</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default ProcessDetail
