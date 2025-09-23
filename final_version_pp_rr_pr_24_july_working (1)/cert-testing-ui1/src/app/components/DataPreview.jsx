// import { useState, useEffect } from 'react';
// import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
// import { Accordion as UiAccordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
// import { Circle, CheckCircle2, Loader2 } from 'lucide-react';

// export default function DataPreview({ file, data, totalRows, isValidating, isValidated, executionTime, isProcessingGraph, isGraphProcessed, graphExecutionTime, isPolicyUploaded }) {
//   const [currentStep, setCurrentStep] = useState(0);
//   const [graphStep, setGraphStep] = useState(0);

//   const graphSteps = [
//     {
//       title: 'Policy Document Parsing',
//       content: 'Graph-compatible rules for Paid→Paid & Reject→Reject loaded',
//       percentage: '(33%)',
//     },
//     {
//       title: 'Causal Graph Construction',
//       content: 'Nodes and edges created using causal relationships • plan_rule_graph.pkl saved',
//       percentage: '(66%)',
//     },
//     {
//       title: 'Graph Visualization',
//       content: 'Rule logic visually verified using PyVis',
//       percentage: '(100%)',
//     },
//   ];

//   const validationSteps = [
//     {
//       title: 'Claim Mismatch Detection',
//       content: 'Evaluated changes across key claim data fields like TCC, patient pay, and reject codes.',
//       percentage: '(35%)',
//     },
//     {
//       title: 'Field Mapping (Semantic Linkage)',
//       content: 'Mapped claim fields to relevant plan terms using semantic similarity and auto_field_mapping.json to ensure accurate linkage before reasoning.',
//       percentage: '(45%)',
//     },
//     {
//       title: 'Graph-Based Reasoning (FullGraphRAG)',
//       content: 'Retrieved reasoning paths using retrieve_paths_from_graph() with causal flow mapping to rule-based outcomes.',
//       percentage: '(50%)',
//     },
//     {
//       title: 'Validator Prompt Generation',
//       content: 'Injected reasoning paths into the LLM prompt, customized for Paid→Paid and Reject→Reject scenarios.',
//       percentage: '(60%)',
//     },
//     {
//       title: 'LLM-based Explanation Generation',
//       content: 'Produced human-readable justifications for stakeholders, improving interpretability and transparency.',
//       percentage: '(75%)',
//     },
//     {
//       title: 'Agentic Architecture building via LangGraph',
//       content: 'Claims are now routed, validated, and explained through modular nodes within the LangGraph pipeline.',
//       percentage: '(90%)',
//     },
//     {
//       title: 'Batch Claim Validation (Excel Integration)',
//       content: 'Seamless execution of bulk validation integrated directly with Excel input/output processing.',
//       percentage: isValidated ? '(100%)' : '',
//     },
//   ];

//   useEffect(() => {
//     if (isProcessingGraph) {
//       setGraphStep(0);
//       const interval = setInterval(() => {
//         setGraphStep((prev) => {
//           if (prev < graphSteps.length - 1) return prev + 1;
//           return prev;
//         });
//       }, 1000);
//       return () => clearInterval(interval);
//     }
//   }, [isProcessingGraph]);

//   useEffect(() => {
//     if (!isProcessingGraph && isGraphProcessed) {
//       setGraphStep(graphSteps.length - 1);
//     }
//   }, [isProcessingGraph, isGraphProcessed]);

//   useEffect(() => {
//     if (isValidating) {
//       setCurrentStep(0);
//       const interval = setInterval(() => {
//         setCurrentStep((prev) => {
//           if (prev < validationSteps.length - 1) return prev + 1;
//           return prev;
//         });
//       }, 1000);
//       return () => clearInterval(interval);
//     }
//   }, [isValidating]);

//   useEffect(() => {
//     if (!isValidating && isValidated) {
//       setCurrentStep(validationSteps.length - 1);
//     }
//   }, [isValidating, isValidated]);

//   const showGraphProgress = isProcessingGraph || isGraphProcessed;
//   const showValidationProgress = isValidating || isValidated;

//   return (
//     <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 overflow-x-auto">
//       {showGraphProgress && (
//         <UiAccordion type="single" defaultValue="graph-progress" collapsible className="mb-4">
//           <AccordionItem value="graph-progress">
//             <AccordionTrigger className="text-lg font-semibold text-gray-800">
//               {isProcessingGraph ? (
//                 <div className="flex items-center">
//                   <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
//                   Graph Processing in Progress
//                 </div>
//               ) : (
//                 <div className="flex items-center">
//                   <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
//                   Graph Processing Completed in {graphExecutionTime.toFixed(2)} seconds
//                 </div>
//               )}
//             </AccordionTrigger>
//             <AccordionContent>
//               <div className="space-y-4 pt-2">
//                 {graphSteps.slice(0, graphStep + 1).map((step, index) => (
//                   <div key={index} className="flex items-start space-x-3">
//                     {index < graphStep || !isProcessingGraph ? (
//                       <CheckCircle2 className="h-5 w-5 text-green-600 mt-1" />
//                     ) : (
//                       <Circle className="h-5 w-5 text-blue-600 mt-1" fill="currentColor" />
//                     )}
//                     <div className="bg-white p-2 rounded-md shadow-sm flex-grow border border-gray-100">
//                       <p className="font-medium text-gray-700">{step.title}: {step.percentage}</p>
//                       {step.content && <p className="text-sm text-gray-600">{step.content}</p>}
//                     </div>
//                   </div>
//                 ))}
//                 {!isProcessingGraph && isGraphProcessed && (
//                   <div className="mt-4 p-3 bg-green-100 rounded-md text-center text-green-800 font-medium">
//                     Graph generation is complete.
//                   </div>
//                 )}
//               </div>
//             </AccordionContent>
//           </AccordionItem>
//         </UiAccordion>
//       )}
//       {file ? (
//         <UiAccordion type="single" defaultValue="data-table" collapsible>
//           <AccordionItem value="data-table">
//             <AccordionTrigger className="text-lg font-semibold text-gray-800">
//               {data ? (
//                 <div className="flex items-center">
//                   <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
//                   File uploaded: {file.name} (Showing 5 claims of {totalRows})
//                 </div>
//               ) : (
//                 <div className="flex items-center">
//                   <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
//                   Parsing file...
//                 </div>
//               )}
//             </AccordionTrigger>
//             <AccordionContent>
//               {data ? (
//                 <Table className="min-w-full divide-y divide-gray-200">
//                   <TableHeader className="bg-gray-50">
//                     <TableRow>
//                       {Object.keys(data[0]).map((header) => (
//                         <TableHead key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</TableHead>
//                       ))}
//                     </TableRow>
//                   </TableHeader>
//                   <TableBody className="bg-white divide-y divide-gray-200">
//                     {data.map((row, rowIndex) => (
//                       <TableRow key={rowIndex} className="hover:bg-gray-50 transition-colors">
//                         {Object.values(row).map((value, cellIndex) => (
//                           <TableCell key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{value}</TableCell>
//                         ))}
//                       </TableRow>
//                     ))}
//                   </TableBody>
//                 </Table>
//               ) : (
//                 <p className="text-gray-600 text-center">Parsing file...</p>
//               )}
//             </AccordionContent>
//           </AccordionItem>
//         </UiAccordion>
//       ) : (
//         <p className="text-gray-600 text-center my-4">
//           {isPolicyUploaded 
//             ? 'Please upload claims report from the sidebar to begin validation.' 
//             : 'Please upload a plan documents & claims report from the sidebar to begin validation.'}
//         </p>
//       )}
//       {showValidationProgress && (
//         <UiAccordion type="single" defaultValue="validation-progress" collapsible className="mt-4">
//           <AccordionItem value="validation-progress">
//             <AccordionTrigger className="text-lg font-semibold text-gray-800">
//               {isValidating ? (
//                 <div className="flex items-center">
//                   <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
//                   Validation in Progress
//                 </div>
//               ) : (
//                 <div className="flex items-center">
//                   <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
//                   Validation Completed in {executionTime.toFixed(2)} seconds
//                 </div>
//               )}
//             </AccordionTrigger>
//             <AccordionContent>
//               <div className="space-y-4 pt-2">
//                 {validationSteps.slice(0, currentStep + 1).map((step, index) => (
//                   <div key={index} className="flex items-start space-x-3">
//                     {index < currentStep || !isValidating ? (
//                       <CheckCircle2 className="h-5 w-5 text-green-600 mt-1" />
//                     ) : (
//                       <Circle className="h-5 w-5 text-blue-600 mt-1" fill="currentColor" />
//                     )}
//                     <div className="bg-white p-2 rounded-md shadow-sm flex-grow border border-gray-100">
//                       <p className="font-medium text-gray-700">{step.title}: {step.percentage}</p>
//                       {step.content && <p className="text-sm text-gray-600">{step.content}</p>}
//                     </div>
//                   </div>
//                 ))}
//                 {!isValidating && isValidated && (
//                   <div className="mt-4 p-3 bg-green-100 rounded-md text-center text-green-800 font-medium">
//                     Validation is complete.
//                   </div>
//                 )}
//               </div>
//             </AccordionContent>
//           </AccordionItem>
//         </UiAccordion>
//       )}
//     </div>
//   );
// }


import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Accordion as UiAccordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Circle, CheckCircle2, Loader2 } from 'lucide-react';

export default function DataPreview({ file, data, totalRows, isValidating, isValidated, executionTime, isProcessingGraph, isGraphProcessed, graphExecutionTime, isPolicyUploaded }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [graphStep, setGraphStep] = useState(0);

  const graphSteps = [
    {
      title: 'Policy Document Parsing',
      content: 'Graph-compatible rules for Paid→Paid & Reject→Reject loaded',
      percentage: '(33%)',
    },
    {
      title: 'Causal Graph Construction',
      content: 'Nodes and edges created using causal relationships • plan_rule_graph.pkl saved',
      percentage: '(66%)',
    },
    {
      title: 'Graph Visualization',
      content: 'Rule logic visually verified using PyVis',
      percentage: isGraphProcessed ? '(100%)' : '',
    },
  ];

  const validationSteps = [
    {
      title: 'Claim Mismatch Detection',
      content: 'Evaluated changes across key claim data fields like TCC, patient pay, and reject codes.',
      percentage: '(35%)',
    },
    {
      title: 'Field Mapping (Semantic Linkage)',
      content: 'Mapped claim fields to relevant plan terms using semantic similarity and auto_field_mapping.json to ensure accurate linkage before reasoning.',
      percentage: '(45%)',
    },
    {
      title: 'Graph-Based Reasoning (FullGraphRAG)',
      content: 'Retrieved reasoning paths using retrieve_paths_from_graph() with causal flow mapping to rule-based outcomes.',
      percentage: '(50%)',
    },
    {
      title: 'Validator Prompt Generation',
      content: 'Injected reasoning paths into the LLM prompt, customized for Paid→Paid and Reject→Reject scenarios.',
      percentage: '(60%)',
    },
    {
      title: 'LLM-based Explanation Generation',
      content: 'Produced human-readable justifications for stakeholders, improving interpretability and transparency.',
      percentage: '(75%)',
    },
    {
      title: 'Agentic Architecture building via LangGraph',
      content: 'Claims are now routed, validated, and explained through modular nodes within the LangGraph pipeline.',
      percentage: '(90%)',
    },
    {
      title: 'Batch Claim Validation (Excel Integration)',
      content: 'Seamless execution of bulk validation integrated directly with Excel input/output processing.',
      percentage: isValidated ? '(100%)' : '',
    },
  ];

  useEffect(() => {
    if (isProcessingGraph) {
      setGraphStep(0);
      const interval = setInterval(() => {
        setGraphStep((prev) => {
          if (prev < graphSteps.length - 1) return prev + 1;
          return prev;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isProcessingGraph]);

  useEffect(() => {
    if (!isProcessingGraph && isGraphProcessed) {
      setGraphStep(graphSteps.length - 1);
    }
  }, [isProcessingGraph, isGraphProcessed]);

  useEffect(() => {
    if (isValidating) {
      setCurrentStep(0);
      const interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < validationSteps.length - 1) return prev + 1;
          return prev;
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isValidating]);

  useEffect(() => {
    if (!isValidating && isValidated) {
      setCurrentStep(validationSteps.length - 1);
    }
  }, [isValidating, isValidated]);

  const showGraphProgress = isProcessingGraph || isGraphProcessed;
  const showValidationProgress = isValidating || isValidated;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 overflow-x-auto">
      {showGraphProgress && (
        <UiAccordion type="single" defaultValue="graph-progress" collapsible className="mb-4">
          <AccordionItem value="graph-progress">
            <AccordionTrigger className="text-lg font-semibold text-gray-800">
              {isProcessingGraph ? (
                <div className="flex items-center">
                  <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
                  Graph Processing in Progress
                </div>
              ) : (
                <div className="flex items-center">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
                  Graph Processing Completed in {graphExecutionTime.toFixed(2)} seconds
                </div>
              )}
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-2">
                {graphSteps.slice(0, graphStep + 1).map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    {index < graphStep || !isProcessingGraph ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600 mt-1" />
                    ) : (
                      <Circle className="h-5 w-5 text-blue-600 mt-1" fill="currentColor" />
                    )}
                    <div className="bg-white p-2 rounded-md shadow-sm flex-grow border border-gray-100">
                      <p className="font-medium text-gray-700">{step.title}: {step.percentage}</p>
                      {step.content && <p className="text-sm text-gray-600">{step.content}</p>}
                    </div>
                  </div>
                ))}
                {!isProcessingGraph && isGraphProcessed && (
                  <div className="mt-4 p-3 bg-green-100 rounded-md text-center text-green-800 font-medium">
                    Graph generation is complete.
                  </div>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        </UiAccordion>
      )}
      {file ? (
        <UiAccordion type="single" defaultValue="data-table" collapsible>
          <AccordionItem value="data-table">
            <AccordionTrigger className="text-lg font-semibold text-gray-800">
              {data ? (
                <div className="flex items-center">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
                  File uploaded: {file.name} (Showing 5 claims of {totalRows})
                </div>
              ) : (
                <div className="flex items-center">
                  <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
                  Parsing file...
                </div>
              )}
            </AccordionTrigger>
            <AccordionContent>
              {data ? (
                <Table className="min-w-full divide-y divide-gray-200">
                  <TableHeader className="bg-gray-50">
                    <TableRow>
                      {Object.keys(data[0]).map((header) => (
                        <TableHead key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody className="bg-white divide-y divide-gray-200">
                    {data.map((row, rowIndex) => (
                      <TableRow key={rowIndex} className="hover:bg-gray-50 transition-colors">
                        {Object.values(row).map((value, cellIndex) => (
                          <TableCell key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{value}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-gray-600 text-center">Parsing file...</p>
              )}
            </AccordionContent>
          </AccordionItem>
        </UiAccordion>
      ) : (
        <p className="text-gray-600 text-center my-4">
          {isPolicyUploaded 
            ? 'Please upload claims report from the sidebar to begin validation.' 
            : 'Please upload a plan documents & claims report from the sidebar to begin validation.'}
        </p>
      )}
      {showValidationProgress && (
        <UiAccordion type="single" defaultValue="validation-progress" collapsible className="mt-4">
          <AccordionItem value="validation-progress">
            <AccordionTrigger className="text-lg font-semibold text-gray-800">
              {isValidating ? (
                <div className="flex items-center">
                  <Loader2 className="h-5 w-5 animate-spin text-[#FB4E0B] mr-2" />
                  Validation in Progress
                </div>
              ) : (
                <div className="flex items-center">
                  <CheckCircle2 className="h-5 w-5 text-green-600 mr-2" />
                  Validation Completed in {executionTime.toFixed(2)} seconds
                </div>
              )}
            </AccordionTrigger>
            <AccordionContent>
              <div className="space-y-4 pt-2">
                {validationSteps.slice(0, currentStep + 1).map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    {index < currentStep || !isValidating ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600 mt-1" />
                    ) : (
                      <Circle className="h-5 w-5 text-blue-600 mt-1" fill="currentColor" />
                    )}
                    <div className="bg-white p-2 rounded-md shadow-sm flex-grow border border-gray-100">
                      <p className="font-medium text-gray-700">{step.title}: {step.percentage}</p>
                      {step.content && <p className="text-sm text-gray-600">{step.content}</p>}
                    </div>
                  </div>
                ))}
                {!isValidating && isValidated && (
                  <div className="mt-4 p-3 bg-green-100 rounded-md text-center text-green-800 font-medium">
                    Validation is complete.
                  </div>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        </UiAccordion>
      )}
    </div>
  );
}