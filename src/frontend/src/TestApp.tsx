// Simple test app to verify basic functionality
import { useState } from 'react';
import { ChaoticButton } from './components/atomic/ChaoticButton';

export default function TestApp() {
  const [count, setCount] = useState(0);

  return (
    <div style={{ padding: '20px', minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <h1 style={{ color: 'white', textAlign: 'center', marginBottom: '40px' }}>
        🎭 SmartHistory Dadaist Frontend Test
      </h1>
      
      <div style={{ textAlign: 'center' }}>
        <ChaoticButton 
          variant="primary" 
          size="large" 
          onClick={() => setCount(count + 1)}
        >
          🎨 Clicked {count} times
        </ChaoticButton>
        
        <div style={{ marginTop: '20px' }}>
          <ChaoticButton variant="chaos" chaos={0.9}>
            Maximum Chaos
          </ChaoticButton>
        </div>
        
        <div style={{ marginTop: '20px' }}>
          <ChaoticButton variant="harmony" chaos={0.3}>
            Minimal Chaos
          </ChaoticButton>
        </div>
      </div>
      
      <div style={{ marginTop: '40px', color: 'white', textAlign: 'center' }}>
        <p>If you can see this and the buttons work, the Dadaist frontend is functioning! 🎉</p>
        <p>Count: {count}</p>
      </div>
    </div>
  );
}