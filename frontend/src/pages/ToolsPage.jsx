import React from 'react';
import ToolList from '../components/ToolList';
import { useTools } from '../hooks/useTools';

function ToolsPage() {
  const { tools } = useTools();

  return (
    <div>
      <h1>Available Tools</h1>
      <ToolList tools={tools} />
    </div>
  );
}

export default ToolsPage;
