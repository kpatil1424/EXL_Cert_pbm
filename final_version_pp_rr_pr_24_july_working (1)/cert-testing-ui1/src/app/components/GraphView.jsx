import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';

export default function GraphView({validationData}) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  if (!validationData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <p className="text-gray-500 text-center">(Graph will be available once validation is run)</p>
      </div>
    )
  }

  const handleLoad = () => setLoading(false);

  const handleError = () => {
    setLoading(false);
    setError('Failed to load the graph HTML. Ensure the file exists in public/output/.');
  };

  return (
    <Card className="shadow-md">
      <CardContent className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Custom Rule Graph Visualization</h3>
        <p className="text-sm text-gray-600 mb-4"></p>
        {loading && <p className="text-gray-500 text-center">Loading graph</p>}
        {error && <p className="text-red-500 text-center">{error}</p>}
        <iframe
          src="/plan_rule_graph.html"
          width="100%"
          height="750px"
          frameBorder="0" 
          onLoad={handleLoad}
          onError={handleError}
          className="rounded-md border border-gray-200"
          title="Custom Graph Visualization"
        />
      </CardContent>
    </Card>
  );
}
