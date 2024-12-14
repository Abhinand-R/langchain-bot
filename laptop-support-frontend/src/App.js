import React, { useState } from 'react';
import axios from 'axios';

// Remove TypeScript interfaces, use prop types if needed

const LaptopSupportChatbot = () => {
  // State management remains the same
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');
  const [context, setContext] = useState('product_inquiry');
  const [isLoading, setIsLoading] = useState(false);

  // Handle query submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;

    // User message object
    const userMessage = {
      type: 'user',
      text: query,
      context: context
    };

    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      // Send request to backend
      const response = await axios.post('http://localhost:8000/support', {
        context,
        query
      });

      // Bot response object
      const botMessage = {
        type: 'bot',
        text: response.data.response,
        context: response.data.context
      };

      setMessages(prevMessages => [...prevMessages, botMessage]);
      setQuery(''); // Clear input
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Error message object
      const errorMessage = {
        type: 'bot',
        text: 'Sorry, there was an error processing your request.',
        context: 'error'
      };

      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-md bg-white rounded-xl shadow-md overflow-hidden">
        <div className="bg-blue-500 text-white text-center py-4">
          <h1 className="text-2xl font-bold">Laptop Support Chatbot</h1>
        </div>

        {/* Chat Messages Container */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`flex ${
                message.type === 'user' 
                  ? 'justify-end' 
                  : 'justify-start'
              }`}
            >
              <div 
                className={`max-w-[80%] p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-black'
                }`}
              >
                {message.text}
                {message.context && (
                  <span 
                    className="block text-xs mt-1 opacity-70"
                  >
                    Context: {message.context}
                  </span>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="text-center text-gray-500">
              Generating response...
            </div>
          )}
        </div>

        {/* Input Form */}
        <form 
          onSubmit={handleSubmit} 
          className="p-4 bg-gray-50 border-t flex items-center"
        >
          <select
            value={context}
            onChange={(e) => setContext(e.target.value)}
            className="mr-2 p-2 border rounded"
          >
            <option value="product_inquiry">Product Inquiry</option>
            <option value="technical">Technical Support</option>
            <option value="billing">Billing</option>
          </select>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question..."
            className="flex-grow p-2 border rounded mr-2"
          />

          <button 
            type="submit" 
            disabled={isLoading}
            className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default LaptopSupportChatbot;