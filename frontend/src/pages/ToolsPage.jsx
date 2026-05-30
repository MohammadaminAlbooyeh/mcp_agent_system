import React, { useState, useEffect } from 'react';
import ToolList from '../components/ToolList';

function ToolsPage() {
  const [tools, setTools] = useState([]);

  useEffect(() => {
    fetch('/api/tools')
      .then(res => res.json())
      .then(setTools)
      .catch(console.error);
  }, []);

  return (
    <div>
      <h1>Available Tools</h1>
      <ToolList tools={tools} />
    </div>
  );
}

export default ToolsPage;
