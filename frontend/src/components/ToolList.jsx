import React from 'react';

function ToolList({ tools }) {
  const categories = {};
  tools.forEach(tool => {
    const category = tool.name?.split('_')[0] || 'other';
    if (!categories[category]) categories[category] = [];
    categories[category].push(tool);
  });

  return (
    <div style={{ marginTop: 16 }}>
      {Object.entries(categories).map(([category, categoryTools]) => (
        <div key={category} style={{ marginBottom: 24 }}>
          <h3 style={{ textTransform: 'capitalize', marginBottom: 12 }}>{category}</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
            {categoryTools.map(tool => (
              <div key={tool.name} className="card">
                <h4>{tool.name}</h4>
                <p style={{ color: '#666', fontSize: 13, marginTop: 8 }}>{tool.description}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
      {tools.length === 0 && <p>No tools available</p>}
    </div>
  );
}

export default ToolList;
