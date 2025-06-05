import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { CheckCircle, AlertCircle, Globe, BookOpen, GraduationCap, FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'

function SearchResults({ results }) {
  const [expandedSources, setExpandedSources] = useState({})

  if (!results) return null

  const toggleSource = (source) => {
    setExpandedSources(prev => ({
      ...prev,
      [source]: !prev[source]
    }))
  }

  const getSourceIcon = (source) => {
    switch (source) {
      case 'arxiv_search':
        return <FileText className="h-5 w-5 text-purple-600" />
      case 'wikipedia_search':
        return <BookOpen className="h-5 w-5 text-blue-600" />
      case 'google_scholar_search':
        return <GraduationCap className="h-5 w-5 text-green-600" />
      case 'google_search':
        return <Globe className="h-5 w-5 text-orange-600" />
      default:
        return <Globe className="h-5 w-5 text-gray-600" />
    }
  }

  return (
    <div className="space-y-6">
      {/* 主要答案 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-start space-x-3 mb-4">
          {results.success ? (
            <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
          ) : (
            <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0 mt-1" />
          )}
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {results.success ? '搜索结果' : '搜索失败'}
            </h2>
            {results.success && results.iterations && (
              <p className="text-sm text-gray-500">
                经过 {results.iterations} 轮迭代搜索
              </p>
            )}
          </div>
        </div>

        {results.success ? (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{results.answer || '未找到相关信息'}</ReactMarkdown>
          </div>
        ) : (
          <div className="text-red-600">
            {results.error || '发生未知错误'}
          </div>
        )}
      </div>

      {/* 搜索来源详情 */}
      {results.success && results.search_results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">信息来源</h3>
          <div className="space-y-3">
            {Object.entries(results.search_results).map(([query, data]) => (
              <div key={query} className="border rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleSource(query)}
                  className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3">
                    {getSourceIcon(data.tool)}
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{query}</p>
                      <p className="text-sm text-gray-500">使用 {data.tool}</p>
                    </div>
                  </div>
                  {expandedSources[query] ? (
                    <ChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </button>

                {expandedSources[query] && (
                  <div className="p-4 bg-white border-t">
                    {data.error ? (
                      <p className="text-red-600">错误: {data.error}</p>
                    ) : (
                      <div className="space-y-3">
                        {typeof data.results === 'string' ? (
                          <div className="text-sm text-gray-700 whitespace-pre-wrap">
                            {data.results}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-700">
                            <pre className="bg-gray-50 p-3 rounded overflow-auto">
                              {JSON.stringify(data.results, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SearchResults 