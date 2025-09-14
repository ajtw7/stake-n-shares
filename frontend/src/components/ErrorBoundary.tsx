import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      return (
        <div style={{padding:16, border:'1px solid #822', background:'#200', color:'#faa', borderRadius:6}}>
          <h3 style={{marginTop:0}}>UI Error</h3>
          <pre style={{whiteSpace:'pre-wrap'}}>{this.state.error.message}</pre>
          <button onClick={this.reset}>Retry</button>
        </div>
      );
    }
    return this.props.children;
  }
}