import { Component } from 'react';
import ChatInterface from './components/ChatInterface';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-100 text-red-800 border-l-4 border-red-500">
          <h1 className="font-bold text-lg">⚠️ Something went wrong.</h1>
          <pre className="mt-2 text-sm overflow-auto">{this.state.error?.toString()}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  return (
    <div className="App">
      <ErrorBoundary>
        <ChatInterface />
      </ErrorBoundary>
    </div>
  );
}

export default App;
