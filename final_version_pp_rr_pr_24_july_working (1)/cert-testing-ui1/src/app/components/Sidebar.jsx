import { useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChevronLeft, ChevronRight, Upload as UploadIcon, Play, FileText } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export default function Sidebar({ file, setFile, policyFile, setPolicyFile, onProcessGraph, onRunValidation, isSidebarOpen, setIsSidebarOpen, isGraphProcessed }) {
  const claimsInputRef = useRef(null);
  const policyInputRef = useRef(null);

  const handleClaimsDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/json' || droppedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      if (droppedFile.size <= 200 * 1024 * 1024) {
        setFile(droppedFile);
      } else {
        alert('File exceeds 200MB limit.');
      }
    } else {
      alert('Invalid file type. Only JSON and XLSX are allowed.');
    }
  };

  const handleClaimsChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size <= 200 * 1024 * 1024) {
        setFile(selectedFile);
      } else {
        alert('File exceeds 200MB limit.');
      }
    }
  };

  const handlePolicyDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.size <= 200 * 1024 * 1024) {
      setPolicyFile(droppedFile);
    } else {
      alert('File exceeds 200MB limit.');
    }
  };

  const handlePolicyChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size <= 200 * 1024 * 1024) {
        setPolicyFile(selectedFile);
      } else {
        alert('File exceeds 200MB limit.');
      }
    }
  };

  const truncateName = (name, maxLength = 35) => {
    if (name.length <= maxLength) return name;
    return name.slice(0, maxLength - 3) + '...';
  };

  return (
    <TooltipProvider>
      <div className={`flex-shrink-0 p-4 bg-white border-r border-gray-200 transition-all duration-300 ${isSidebarOpen ? 'w-80' : 'w-16'}`}>
        <div className="flex items-center justify-between mb-6">
          {isSidebarOpen ? (
            <div className="flex flex-col">
              <img 
                src="https://companieslogo.com/img/orig/EXLS-d1ce9a1c.png" 
                alt="EXL" 
                className="h-8 mb-1" 
              />
              <span className="text-lg font-semibold text-gray-800">Cert Testing</span>
            </div>
          ) : null}
          <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </Button>
        </div>
        {isSidebarOpen ? (
          <>
            <Card className="mb-4 shadow-md border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg font-semibold text-gray-800">Upload Policy Document</CardTitle>
                <Tooltip>
                  <TooltipTrigger><span className="text-gray-500 cursor-help">ⓘ</span></TooltipTrigger>
                  <TooltipContent>Upload a document file (PDF recommended)</TooltipContent>
                </Tooltip>
              </CardHeader>
              <CardContent>
                <div
                  className="border-2 border-dashed border-gray-300 p-4 mb-4 text-center rounded-md bg-gray-50 hover:border-[#FB4E0B] transition-colors"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handlePolicyDrop}
                >
                  <p className="text-sm font-medium text-gray-600">Drag and drop file here</p>
                  <p className="text-xs text-gray-500">Limit 200MB per file · Any document</p>
                </div>
                {policyFile && (
                  <div className="mb-4 text-sm text-gray-600">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-pointer">{truncateName(policyFile.name)}</span>
                      </TooltipTrigger>
                      <TooltipContent>{policyFile.name}</TooltipContent>
                    </Tooltip>
                  </div>
                )}
                <Button onClick={() => policyInputRef.current.click()} className="w-full bg-gray-700 hover:bg-gray-800 text-white">
                  Browse file
                </Button>
                <input
                  type="file"
                  ref={policyInputRef}
                  className="hidden"
                  onChange={handlePolicyChange}
                  accept="*/*"
                />
              </CardContent>
            </Card>
            <Button onClick={onProcessGraph} className="w-full bg-[#FB4E0B] hover:bg-[#D93E0A] text-white mb-4" disabled={!policyFile}>
              Process Network Graph
            </Button>
            <Card className="mb-4 shadow-md border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-lg font-semibold text-gray-800">Upload Claims Data</CardTitle>
                <Tooltip>
                  <TooltipTrigger><span className="text-gray-500 cursor-help">ⓘ</span></TooltipTrigger>
                  <TooltipContent>Upload JSON or XLSX files for validation</TooltipContent>
                </Tooltip>
              </CardHeader>
              <CardContent>
                <div
                  className="border-2 border-dashed border-gray-300 p-4 mb-4 text-center rounded-md bg-gray-50 hover:border-[#FB4E0B] transition-colors"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={handleClaimsDrop}
                >
                  <p className="text-sm font-medium text-gray-600">Drag and drop file here</p>
                  <p className="text-xs text-gray-500">Limit 200MB per file · JSON, XLSX</p>
                </div>
                {file && (
                  <div className="mb-4 text-sm text-gray-600">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="cursor-pointer">{truncateName(file.name)}</span>
                      </TooltipTrigger>
                      <TooltipContent>{file.name}</TooltipContent>
                    </Tooltip>
                  </div>
                )}
                <Button onClick={() => claimsInputRef.current.click()} className="w-full bg-gray-700 hover:bg-gray-800 text-white">
                  Browse file
                </Button>
                <input
                  type="file"
                  ref={claimsInputRef}
                  className="hidden"
                  onChange={handleClaimsChange}
                  accept=".json,.xlsx"
                />
              </CardContent>
            </Card>
            <Button onClick={onRunValidation} className="w-full bg-[#FB4E0B] hover:bg-[#D93E0A] text-white" disabled={!file || !isGraphProcessed}>
              Run Validation
            </Button>
          </>
        ) : (
          <div className="flex flex-col space-y-4">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={() => policyInputRef.current.click()}>
                  <FileText className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Upload Policy Document</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={onProcessGraph} disabled={!policyFile}>
                  <Play className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Process Network Graph</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={() => claimsInputRef.current.click()}>
                  <UploadIcon className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Upload Claims File</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={onRunValidation} disabled={!file || !isGraphProcessed}>
                  <Play className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Run Validation</TooltipContent>
            </Tooltip>
          </div>
        )}
        {/* Hidden inputs for collapsed mode */}
        <input
          type="file"
          ref={claimsInputRef}
          className="hidden"
          onChange={handleClaimsChange}
          accept=".json,.xlsx"
        />
        <input
          type="file"
          ref={policyInputRef}
          className="hidden"
          onChange={handlePolicyChange}
          accept="*/*"
        />
      </div>
    </TooltipProvider>
  );
}