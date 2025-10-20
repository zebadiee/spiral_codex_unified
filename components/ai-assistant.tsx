
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, X, Send, Minimize2, Maximize2 } from 'lucide-react';

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [message, setMessage] = useState('');

  return (
    <>
      {/* Toggle Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 neon-glow-blue shadow-2xl"
          >
            <Bot className="h-6 w-6 text-white" />
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-blue-400"
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Assistant Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ 
              opacity: 1, 
              y: 0, 
              scale: 1,
              height: isMinimized ? 60 : 500 
            }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-6 right-6 z-50 w-96 glass rounded-2xl border border-blue-500/30 shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Bot className="h-5 w-5 text-blue-400" />
                  <motion.div
                    className="absolute -top-1 -right-1 h-2 w-2 bg-green-400 rounded-full"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                </div>
                <span className="font-semibold neon-text-blue">AI Assistant</span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1 hover:bg-blue-500/20 rounded transition-colors"
                >
                  {isMinimized ? (
                    <Maximize2 className="h-4 w-4" />
                  ) : (
                    <Minimize2 className="h-4 w-4" />
                  )}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-red-500/20 rounded transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Content */}
            {!isMinimized && (
              <>
                <div className="h-[360px] p-4 overflow-y-auto custom-scrollbar">
                  <div className="space-y-4">
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex gap-2"
                    >
                      <div className="flex-shrink-0 mt-1">
                        <Bot className="h-5 w-5 text-blue-400" />
                      </div>
                      <div className="flex-1 bg-blue-500/10 rounded-lg p-3 border border-blue-500/20">
                        <p className="text-sm text-slate-300">
                          Hello! I'm your AI assistant. I can help you with:
                        </p>
                        <ul className="mt-2 space-y-1 text-xs text-slate-400">
                          <li>• Generating and enhancing ideas</li>
                          <li>• Project planning and requirements</li>
                          <li>• Architecture recommendations</li>
                          <li>• Timeline estimation</li>
                        </ul>
                      </div>
                    </motion.div>
                  </div>
                </div>

                {/* Input */}
                <div className="p-4 border-t border-blue-500/20">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e?.target?.value ?? '')}
                      placeholder="Ask me anything..."
                      className="flex-1 bg-slate-800/50 border border-blue-500/20 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/50"
                      onKeyPress={(e) => {
                        if (e?.key === 'Enter') {
                          setMessage('');
                        }
                      }}
                    />
                    <button
                      onClick={() => setMessage('')}
                      className="p-2 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors neon-glow-blue"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
