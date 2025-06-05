import React, { useState } from 'react'
import { Search, Loader2, Send } from 'lucide-react'
import axios from 'axios'

function SearchInterface({ onSearch, setIsSearching, isSearching }) {
  const [query, setQuery] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setError(null)
    setIsSearching(true)

    try {
      const response = await axios.post('/api/search', {
        query: query.trim(),
        max_iterations: 3
      })
      onSearch(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || '搜索失败，请稍后重试')
      onSearch({
        success: false,
        error: err.message,
        query: query.trim()
      })
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
            输入您的问题
          </label>
          <div className="relative">
            <textarea
              id="search"
              rows="3"
              className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
              placeholder="例如：大语言模型的最新研究进展是什么？"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isSearching}
            />
            <button
              type="submit"
              disabled={isSearching || !query.trim()}
              className="absolute bottom-3 right-3 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isSearching ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {isSearching && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>正在搜索和分析相关信息...</span>
          </div>
        )}
      </form>

      {/* 示例查询 */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-sm text-gray-600 mb-3">试试这些查询：</p>
        <div className="flex flex-wrap gap-2">
          {[
            "量子计算的最新突破",
            "人工智能在医疗领域的应用",
            "气候变化的最新研究",
            "SpaceX星舰的技术原理"
          ].map((example) => (
            <button
              key={example}
              onClick={() => setQuery(example)}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default SearchInterface 