import { Card, CardContent } from '@/components/ui/card';

export default function AgenticAIOverview() {
  return (
    <Card className="shadow-md">
      <CardContent className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Agentic AI Overview</h3>
        <p className="text-sm text-gray-600 mb-4">
          This tab explains the agentic AI method used to build our Proof of Concept (POC). Agentic AI enables autonomous systems to handle complex tasks with minimal supervision, adapting in real-time to achieve goals[3][4].
        </p>
        
        <section className="mb-6">
          <h4 className="text-md font-medium text-gray-700 mb-2">What is Agentic AI?</h4>
          <p className="text-sm text-gray-600 mb-2">
            Agentic AI refers to intelligent systems that can perceive their environment, reason about tasks, act independently, and learn from feedback to solve multi-step problems[2][5]. Unlike traditional AI, it operates with agency, making decisions dynamically.
          </p>
          <ul className="list-disc pl-5 text-sm text-gray-600">
            <li><strong>Perceive:</strong> Gathers and processes data from various sources[2].</li>
            <li><strong>Reason:</strong> Uses LLMs to plan and sequence tasks[2][5].</li>
            <li><strong>Act:</strong> Executes actions via tools and APIs[2].</li>
            <li><strong>Learn:</strong> Improves through feedback loops[2][5].</li>
          </ul>
        </section>
        
        <section className="mb-6">
          <h4 className="text-md font-medium text-gray-700 mb-2">How We Used Agentic AI in This POC</h4>
          <p className="text-sm text-gray-600 mb-2">
            In our POC, agentic AI automates claim validation by routing data through modular agents that detect mismatches, generate explanations, and integrate with rule graphs[6][9]. This reduces manual effort and enables end-to-end processing.
          </p>
          <div className="bg-gray-100 p-4 rounded-md text-sm text-gray-600">
            <strong>Sample Workflow Diagram (Placeholder):</strong>
            <ul className="list-none">
              <li>Input → Perception Agent → Reasoning Agent → Action Agent → Output</li>
            </ul>
          </div>
        </section>
        
        <section>
          <h4 className="text-md font-medium text-gray-700 mb-2">Benefits and Future Potential</h4>
          <p className="text-sm text-gray-600">
            Agentic AI enhances efficiency by handling dynamic environments, with applications in automation, customer service, and data processing[1][4]. In future iterations, we can expand to multi-agent orchestration for more complex workflows[9].
          </p>
        </section>
      </CardContent>
    </Card>
  );
}
