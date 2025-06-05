import React, { useState } from 'react'
import SearchInterface from './components/SearchInterface'
import SearchResults from './components/SearchResults'
import { Search, Brain, Sparkles } from 'lucide-react'

function App() {
  const [searchResults, setSearchResults] = useState(null)
  const [isSearching, setIsSearching] = useState(false)
  const [searchHistory, setSearchHistory] = useState([])

  const handleSearch = (results) => {
    setSearchResults(results)
    if (results.success) {
      setSearchHistory([...searchHistory, {
        query: results.query,
        timestamp: results.timestamp
      }])
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 头部 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Brain className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">智能搜索Agent</h1>
              <Sparkles className="h-5 w-5 text-yellow-500" />
            </div>
            <div className="text-sm text-gray-500">
              基于LangGraph和Gemini的智能研究助手
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 搜索区域 */}
          <div className="lg:col-span-2">
            <SearchInterface 
              onSearch={handleSearch}
              setIsSearching={setIsSearching}
              isSearching={isSearching}
            />
            
            {/* 搜索结果 */}
            {searchResults && (
              <div className="mt-8">
                <SearchResults results={searchResults} />
              </div>
            )}
          </div>

          {/* 侧边栏 - 搜索历史 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Search className="h-5 w-5 mr-2 text-gray-500" />
                搜索历史
              </h3>
              {searchHistory.length === 0 ? (
                <p className="text-gray-500 text-sm">暂无搜索记录</p>
              ) : (
                <ul className="space-y-2">
                  {searchHistory.slice(-10).reverse().map((item, index) => (
                    <li key={index} className="text-sm">
                      <button
                        className="w-full text-left p-2 rounded hover:bg-gray-50 transition-colors"
                        onClick={() => {
                          // 可以实现点击历史记录重新搜索
                        }}
                      >
                        <div className="font-medium text-gray-700 truncate">
                          {item.query}
                        </div>
                        <div className="text-xs text-gray-400">
                          {new Date(item.timestamp).toLocaleString('zh-CN')}
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* 功能说明 */}
            <div className="bg-white rounded-lg shadow-md p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">功能特性</h3>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>多源智能搜索：arXiv、Wikipedia、Google Scholar、Google Search</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>迭代式搜索：自动识别信息差距并补充搜索</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>智能分析：基于Gemini的深度理解和总结</span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>引用来源：所有信息都标注可靠来源</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App 