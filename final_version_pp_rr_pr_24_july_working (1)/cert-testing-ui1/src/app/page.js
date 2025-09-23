// // App.jsx (updated to revert formData key to 'file' and remove policy appending)
// 'use client';
// import { useState, useEffect } from 'react';
// import Sidebar from './components/Sidebar';
// import DataPreview from './components/DataPreview';
// import ValidationResults from './components/ValidationResults';
// import GraphView from './components/GraphView';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import * as XLSX from 'xlsx';
// import AgenticAIOverview from './components/AgenticAIOverview';

// function App() {
//   const [file, setFile] = useState(null);
//   const [policyFile, setPolicyFile] = useState(null); // Changed to single file
//   const [previewData, setPreviewData] = useState(null);
//   const [totalRows, setTotalRows] = useState(0);
//   const [validationData, setValidationData] = useState(null);
//   const [humanReviewData, setHumanReviewData] = useState({
//     paid_paid: {
//       valid: { data: [], count: 0 },
//       invalid: { data: [], count: 0 },
//       error: { data: [], count: 0 },
//       total_count: 0,
//     },
//     reject_reject: {
//       valid: { data: [], count: 0 },
//       invalid: { data: [], count: 0 },
//       error: { data: [], count: 0 },
//       total_count: 0,
//     },
//     paid_reject: {
//       valid: { data: [], count: 0 },
//       invalid: { data: [], count: 0 },
//       error: { data: [], count: 0 },
//       total_count: 0,
//     },
//   });
//   const [executionTime, setExecutionTime] = useState(0);
//   const [isValidating, setIsValidating] = useState(false);
//   const [isValidated, setIsValidated] = useState(false);
//   const [activeTab, setActiveTab] = useState('data-preview');
//   const [isSidebarOpen, setIsSidebarOpen] = useState(true);
//   const [isProcessingGraph, setIsProcessingGraph] = useState(false);
//   const [isGraphProcessed, setIsGraphProcessed] = useState(false);
//   const [graphExecutionTime, setGraphExecutionTime] = useState(0);

//   useEffect(() => {
//     if (file) {
//       const reader = new FileReader();
//       reader.onload = (e) => {
//         try {
//           let parsedData;
//           if (file.type === 'application/json') {
//             parsedData = JSON.parse(e.target.result);
//             if (!Array.isArray(parsedData)) {
//               parsedData = [parsedData];
//             }
//           } else {
//             const arrayBuffer = e.target.result;
//             const workbook = XLSX.read(arrayBuffer, { type: 'array' });
//             const sheetName = workbook.SheetNames[0];
//             const sheet = workbook.Sheets[sheetName];
//             parsedData = XLSX.utils.sheet_to_json(sheet);
//           }
//           setPreviewData(parsedData.slice(0, 5));
//           setTotalRows(parsedData.length);
//         } catch (err) {
//           alert('Error parsing file: ' + err.message);
//           setPreviewData(null);
//           setTotalRows(0);
//         }
//       };
//       if (file.type === 'application/json') {
//         reader.readAsText(file);
//       } else {
//         reader.readAsArrayBuffer(file);
//       }
//     } else {
//       setPreviewData(null);
//       setTotalRows(0);
//     }
//   }, [file]);

//   const handleProcessGraph = async () => {
//     if (!policyFile) {
//       alert('Please upload a policy document first.');
//       return;
//     }
//     setIsProcessingGraph(true);
//     setActiveTab('data-preview'); // Switch to data preview to show progress
//     const startTime = Date.now();
//     const formData = new FormData();
//     formData.append('file', policyFile);
//     try {
      
//       // const response = await fetch('https://pbmtesting-bck-evb7d0cpbpb6ggh8.canadacentral-01.azurewebsites.net/api/upload_pbm_document', {
//       const response = await fetch('https://8000-01jzzercf6hf1txhgmsmsv7axx.cloudspaces.litng.ai/api/upload_pbm_document', {
//         method: 'POST',
//         body: formData,
//       });
//       if (!response.ok) {
//         const errorText = await response.text();
//         throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
//       }
//       const result = await response.json();
//       if (result.status === 'success') {
//         setIsGraphProcessed(true);
//         setGraphExecutionTime((Date.now() - startTime) / 1000);
//       } else {
//         alert('Graph processing error: ' + result.message);
//       }
//     } catch (error) {
//       console.error('Graph processing error:', error);
//       alert('Error during graph processing: ' + error.message);
//     } finally {
//       setIsProcessingGraph(false);
//     }
//   };

//   const handleRunValidation = async () => {
//     if (!file) {
//       alert('Please upload a claims file first.');
//       return;
//     }
//     setIsValidating(true);
//     setValidationData(null);
//     setIsValidated(false);
//     setActiveTab('data-preview');
//     const formData = new FormData();
//     formData.append('file', file);
//     try {
//       // const response = await fetch('https://pbmtesting-bck-evb7d0cpbpb6ggh8.canadacentral-01.azurewebsites.net/api/validate', {
//       const response = await fetch('https://8000-01jzzercf6hf1txhgmsmsv7axx.cloudspaces.litng.ai/api/validate', {
//         method: 'POST',
//         body: formData,
//       });
//       if (!response.ok) {
//         const errorText = await response.text();
//         throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
//       }
//       const result = await response.json();
//       if (result.status === 'success') {
//         setValidationData(result.data);
//         setExecutionTime(result.execution_time);
//         setIsValidated(true);
//       } else {
//         alert('Validation error: ' + result.message);
//       }
//     } catch (error) {
//       console.error('Validation error:', error);
//       alert('Error during validation: ' + error.message);
//     } finally {
//       setIsValidating(false);
//     }
//   };

//   const handleAddToReview = (selectedRows) => {
//     setHumanReviewData((prev) => {
//       const newData = JSON.parse(JSON.stringify(prev));
//       selectedRows.forEach((row) => {
//         const claimKey = row['Claim Type'].toLowerCase().replace('→', '_');
//         let validKey = row['Outcome'].toLowerCase();
//         if (validKey === "valid_mismatch") validKey = "valid";
//         else if (validKey === "invalid_mismatch") validKey = "invalid";
//         else if (validKey === "error") validKey = "error";
//         if (!newData[claimKey]) {
//           newData[claimKey] = {};
//         }
//         if (!newData[claimKey][validKey]) {
//           newData[claimKey][validKey] = { data: [], count: 0 };
//         }
//         const bucket = newData[claimKey][validKey];
//         if (!bucket.data.some((r) => r.PRE_RXCLAIM_NUMBER === row.PRE_RXCLAIM_NUMBER)) {
//           bucket.data.push(row);
//           bucket.count++;
//           newData[claimKey].total_count = (newData[claimKey].total_count || 0) + 1;
//         }
//       });
//       return newData;
//     });
//   };

//   return (
//     <div className="flex h-screen bg-gray-100">
//       <Sidebar
//         file={file}
//         setFile={setFile}
//         policyFile={policyFile}
//         setPolicyFile={setPolicyFile}
//         onProcessGraph={handleProcessGraph}
//         onRunValidation={handleRunValidation}
//         isSidebarOpen={isSidebarOpen}
//         setIsSidebarOpen={setIsSidebarOpen}
//         isGraphProcessed={isGraphProcessed}
//       />
//       <div className="flex-1 p-8 overflow-auto bg-gray-100">
//         <Tabs value={activeTab} onValueChange={setActiveTab} className="bg-white rounded-lg shadow-md p-4">
//           <TabsList className="border-b mb-4">
//             <TabsTrigger value="data-preview" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Data Preview</TabsTrigger>
//             <TabsTrigger value="validation-results" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Validation Results</TabsTrigger>
//             <TabsTrigger value="human-review" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Human Review Claims</TabsTrigger>
//             <TabsTrigger value="rule-graph" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Rule Graph</TabsTrigger>
//             <TabsTrigger value="agentic-ai" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Agentic AI Overview</TabsTrigger>
//           </TabsList>
//           <TabsContent value="data-preview" className="pt-0">
//             <DataPreview 
//               file={file} 
//               data={previewData} 
//               totalRows={totalRows} 
//               isValidating={isValidating} 
//               isValidated={isValidated} 
//               executionTime={executionTime}
//               isProcessingGraph={isProcessingGraph}
//               isGraphProcessed={isGraphProcessed}
//               graphExecutionTime={graphExecutionTime}
//               isPolicyUploaded={!!policyFile}
//             />
//           </TabsContent>
//           <TabsContent value="validation-results" className="pt-0">
//             <ValidationResults 
//               validationData={validationData} 
//               executionTime={executionTime} 
//               onAddToReview={handleAddToReview}
//             />
//           </TabsContent>
//           <TabsContent value="human-review" className="pt-0">
//             <ValidationResults 
//               validationData={humanReviewData} 
//               executionTime={0} 
//               isHumanReview={true}
//             />
//           </TabsContent>
//           <TabsContent value="rule-graph" className="pt-0">
//             <GraphView 
//               validationData={validationData}
//             />
//           </TabsContent>
//           <TabsContent value="agentic-ai" className="pt-0">
//             <AgenticAIOverview validationData={validationData}/>
//           </TabsContent>
//         </Tabs>
//       </div>
//     </div>
//   );
// }

// export default App;


'use client';
import { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import DataPreview from './components/DataPreview';
import ValidationResults from './components/ValidationResults';
import GraphView from './components/GraphView';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import * as XLSX from 'xlsx';
import AgenticAIOverview from './components/AgenticAIOverview';

function App() {
  const [file, setFile] = useState(null);
  const [policyFile, setPolicyFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [totalRows, setTotalRows] = useState(0);
  const [validationData, setValidationData] = useState(null);
  const [humanReviewData, setHumanReviewData] = useState({
    paid_paid: {
      valid: { data: [], count: 0 },
      invalid: { data: [], count: 0 },
      error: { data: [], count: 0 },
      total_count: 0,
    },
    reject_reject: {
      valid: { data: [], count: 0 },
      invalid: { data: [], count: 0 },
      error: { data: [], count: 0 },
      total_count: 0,
    },
    paid_reject: {
      valid: { data: [], count: 0 },
      invalid: { data: [], count: 0 },
      error: { data: [], count: 0 },
      total_count: 0,
    },
  });
  const [executionTime, setExecutionTime] = useState(0);
  const [isValidating, setIsValidating] = useState(false);
  const [isValidated, setIsValidated] = useState(false);
  const [activeTab, setActiveTab] = useState('data-preview');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProcessingGraph, setIsProcessingGraph] = useState(false);
  const [isGraphProcessed, setIsGraphProcessed] = useState(false);
  const [graphExecutionTime, setGraphExecutionTime] = useState(0);
  const scrollContainerRef = useRef(null);

  useEffect(() => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          let parsedData;
          if (file.type === 'application/json') {
            parsedData = JSON.parse(e.target.result);
            if (!Array.isArray(parsedData)) {
              parsedData = [parsedData];
            }
          } else {
            const arrayBuffer = e.target.result;
            const workbook = XLSX.read(arrayBuffer, { type: 'array' });
            const sheetName = workbook.SheetNames[0];
            const sheet = workbook.Sheets[sheetName];
            parsedData = XLSX.utils.sheet_to_json(sheet);
          }
          setPreviewData(parsedData.slice(0, 5));
          setTotalRows(parsedData.length);
        } catch (err) {
          alert('Error parsing file: ' + err.message);
          setPreviewData(null);
          setTotalRows(0);
        }
      };
      if (file.type === 'application/json') {
        reader.readAsText(file);
      } else {
        reader.readAsArrayBuffer(file);
      }
    } else {
      setPreviewData(null);
      setTotalRows(0);
    }
  }, [file]);

  const handleProcessGraph = async () => {
    if (!policyFile) {
      alert('Please upload a policy document first.');
      return;
    }
    setIsProcessingGraph(true);
    setActiveTab('data-preview');
    const startTime = Date.now();
    const formData = new FormData();
    formData.append('file', policyFile);
    try {
      const response = await fetch('https://8000-01jzzercf6hf1txhgmsmsv7axx.cloudspaces.litng.ai/api/upload_pbm_document', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      const result = await response.json();
      if (result.status === 'success') {
        setIsGraphProcessed(true);
        setGraphExecutionTime((Date.now() - startTime) / 1000);
      } else {
        alert('Graph processing error: ' + result.message);
      }
    } catch (error) {
      console.error('Graph processing error:', error);
      alert('Error during graph processing: ' + error.message);
    } finally {
      setIsProcessingGraph(false);
    }
  };

  const handleRunValidation = async () => {
    if (!file) {
      alert('Please upload a claims file first.');
      return;
    }
    setIsValidating(true);
    setValidationData(null);
    setIsValidated(false);
    setActiveTab('data-preview');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('https://8000-01jzzercf6hf1txhgmsmsv7axx.cloudspaces.litng.ai/api/validate', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      const result = await response.json();
      if (result.status === 'success') {
        setValidationData(result.data);
        setExecutionTime(result.execution_time);
        setIsValidated(true);
      } else {
        alert('Validation error: ' + result.message);
      }
    } catch (error) {
      console.error('Validation error:', error);
      alert('Error during validation: ' + error.message);
    } finally {
      setIsValidating(false);
    }
  };

  const handleAddToReview = (selectedRows) => {
    setHumanReviewData((prev) => {
      const newData = JSON.parse(JSON.stringify(prev));
      selectedRows.forEach((row) => {
        const claimKey = row['Claim Type'].toLowerCase().replace('→', '_');
        let validKey = row['Outcome'].toLowerCase();
        if (validKey === "valid_mismatch") validKey = "valid";
        else if (validKey === "invalid_mismatch") validKey = "invalid";
        else if (validKey === "error") validKey = "error";
        if (!newData[claimKey]) {
          newData[claimKey] = {};
        }
        if (!newData[claimKey][validKey]) {
          newData[claimKey][validKey] = { data: [], count: 0 };
        }
        const bucket = newData[claimKey][validKey];
        if (!bucket.data.some((r) => r.PRE_RXCLAIM_NUMBER === row.PRE_RXCLAIM_NUMBER)) {
          bucket.data.push(row);
          bucket.count++;
          newData[claimKey].total_count = (newData[claimKey].total_count || 0) + 1;
        }
      });
      return newData;
    });
  };

  const scrollToTop = () => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        file={file}
        setFile={setFile}
        policyFile={policyFile}
        setPolicyFile={setPolicyFile}
        onProcessGraph={handleProcessGraph}
        onRunValidation={handleRunValidation}
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
        isGraphProcessed={isGraphProcessed}
      />
      <div 
        ref={scrollContainerRef}
        className="flex-1 p-8 overflow-auto bg-gray-100"
      >
        <Tabs value={activeTab} onValueChange={setActiveTab} className="bg-white rounded-lg shadow-md p-4 relative">
          <TabsList className="border-b mb-4">
            <TabsTrigger value="data-preview" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Data Preview</TabsTrigger>
            <TabsTrigger value="validation-results" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Validation Results</TabsTrigger>
            <TabsTrigger value="human-review" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Human Review Claims</TabsTrigger>
            <TabsTrigger value="rule-graph" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Rule Graph</TabsTrigger>
            <TabsTrigger value="agentic-ai" className="data-[state=active]:text-[#FB4E0B] data-[state=active]:border-b-2 data-[state=active]:border-[#FB4E0B]">Agentic AI Overview</TabsTrigger>
          </TabsList>
          <TabsContent value="data-preview" className="pt-0">
            <DataPreview 
              file={file} 
              data={previewData} 
              totalRows={totalRows} 
              isValidating={isValidating} 
              isValidated={isValidated} 
              executionTime={executionTime}
              isProcessingGraph={isProcessingGraph}
              isGraphProcessed={isGraphProcessed}
              graphExecutionTime={graphExecutionTime}
              isPolicyUploaded={!!policyFile}
            />
          </TabsContent>
          <TabsContent value="validation-results" className="pt-0">
            <ValidationResults 
              validationData={validationData} 
              executionTime={executionTime} 
              onAddToReview={handleAddToReview}
            />
          </TabsContent>
          <TabsContent value="human-review" className="pt-0">
            <ValidationResults 
              validationData={humanReviewData} 
              executionTime={0} 
              isHumanReview={true}
            />
          </TabsContent>
          <TabsContent value="rule-graph" className="pt-0">
            <GraphView 
              validationData={validationData}
            />
          </TabsContent>
          <TabsContent value="agentic-ai" className="pt-0">
            <AgenticAIOverview validationData={validationData}/>
          </TabsContent>
          <button
            onClick={scrollToTop}
            className="fixed bottom-6 right-6 bg-[#FB4E0B] text-white p-3 rounded-full shadow-lg hover:bg-[#E5440A] transition-colors"
            title="Scroll to top"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </button>
        </Tabs>
      </div>
    </div>
  );
}

export default App;