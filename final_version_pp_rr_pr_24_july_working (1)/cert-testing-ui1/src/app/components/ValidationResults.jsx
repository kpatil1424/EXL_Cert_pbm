// components/ValidationResults.jsx
import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Checkbox } from '@/components/ui/checkbox';
import { Search } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import * as XLSX from 'xlsx';

export default function ValidationResults({ validationData, executionTime, isHumanReview = false, onAddToReview = () => {} }) {
  const [selectedClaimType, setSelectedClaimType] = useState(null);
  const [selectedValidity, setSelectedValidity] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredClaim, setFilteredClaim] = useState(null);
  const [selectedIndices, setSelectedIndices] = useState([]);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10; // Fixed page size for pagination

  useEffect(() => {
    setSelectedIndices([]);
    setCurrentPage(1); // Reset page on selection change
  }, [selectedClaimType, selectedValidity]);

  if (!validationData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <p className="text-gray-500 text-center">(Validation results would appear here after running validation)</p>
      </div>
    );
  }

  const claimTypeMap = {
    paid_paid: { label: 'Mismatch Paid - Paid', data: validationData.paid_paid },
    reject_reject: { label: 'Mismatch Reject - Reject', data: validationData.reject_reject },
    paid_reject: { label: 'Mismatch Paid - Reject', data: validationData.paid_reject },
  };

  const validityMap = {
    valid: { label: 'Valid Mismatch', color: 'text-gray-900' },
    invalid: { label: 'Invalid Mismatch', color: 'text-gray-900' },
    error: { label: 'Error', color: 'text-gray-900' },
  };

  const downloadResults = () => {
    const allResults = [];
    Object.entries(claimTypeMap).forEach(([claimKey, { data: claimData }]) => {
      Object.entries(claimData).forEach(([validKey, validData]) => {
        if (['valid', 'invalid', 'error'].includes(validKey)) {
          validData.data.forEach((item) => {
            allResults.push({
              ...item,
              claim_type: item.claim_type || claimTypeMap[claimKey].label.replace(/ - /g, '→'),
              valid_mismatch: item.valid_mismatch || validityMap[validKey].label,
            });
          });
        }
      });
    });

    const ws = XLSX.utils.json_to_sheet(allResults);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Results');
    XLSX.writeFile(wb, isHumanReview ? 'Human_Review_Results.xlsx' : 'Validation_Results.xlsx');
  };

  const handleClaimTypeClick = (key) => {
    setSelectedClaimType(selectedClaimType === key ? null : key);
    setSelectedValidity(null);
  };

  const handleValidityClick = (validKey) => {
    setSelectedValidity(selectedValidity === validKey ? null : validKey);
  };

  const handleSearch = (e) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);
    if (query === '') {
      setFilteredClaim(null);
      return;
    }

    let foundClaim = null;
    Object.entries(claimTypeMap).some(([claimKey, { data: claimData }]) => {
      return Object.entries(claimData).some(([validKey, validData]) => {
        if (['valid', 'invalid', 'error'].includes(validKey)) {
          return validData.data.some((item) => {
            if (String(item.PRE_RXCLAIM_NUMBER).toLowerCase() === query) {
              foundClaim = {
                ...item,
                claim_type: item.claim_type || claimTypeMap[claimKey].label.replace(/ - /g, '→'),
                valid_mismatch: item.valid_mismatch || validityMap[validKey].label,
              };
              return true;
            }
            return false;
          });
        }
        return false;
      });
    });

    setFilteredClaim(foundClaim);
  };

  const toggleSelect = (idx) => {
    setSelectedIndices((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]
    );
  };

  const handleAdd = () => {
    const currentData = claimTypeMap[selectedClaimType].data[selectedValidity].data;
    const selectedRows = selectedIndices.map((i) => currentData[i]);
    onAddToReview(selectedRows);
    setSelectedIndices([]);
    setShowConfirmation(true);
    setTimeout(() => setShowConfirmation(false), 3000); // Hide after 3 seconds
  };

  const hasData = Object.values(claimTypeMap).some(({ data }) => data.total_count > 0);

  if (!hasData && isHumanReview) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <p className="text-gray-500 text-center">No claims added for human review yet.</p>
      </div>
    );
  }

  const buttonText = selectedIndices.length > 1 ? 'Add Selected Rows to Human Review' : 'Add Selected Row to Human Review';

  // Pagination logic
  const getPaginatedData = (data) => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
  };

  const totalPages = (dataLength) => Math.ceil(dataLength / pageSize);

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    setSelectedIndices([]); // Reset selections on page change
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        {isHumanReview ? (
          <h3 className="text-lg font-semibold text-gray-800">Human Review Claims</h3>
        ) : (
          <h3 className="text-lg font-semibold text-gray-800">Validation completed in {executionTime.toFixed(2)} seconds.</h3>
        )}
        <Button onClick={downloadResults} variant="outline" className="text-[#FB4E0B] border-[#FB4E0B] hover:bg-[#FB4E0B] hover:text-white">
          Download {isHumanReview ? 'Human Review ' : ''}Results (Excel)
        </Button>
      </div>
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="text"
          placeholder="Search by PRE_RXCLAIM_NUMBER"
          value={searchQuery}
          onChange={handleSearch}
          className="pl-10"
        />
      </div>
      {filteredClaim ? (
        <div className="mb-6">
          <h4 className="text-md font-semibold text-gray-800 mb-2">Search Result</h4>
          <p className="text-sm text-gray-600 mb-2">Claim Type: {filteredClaim.claim_type} | Validity: {filteredClaim.valid_mismatch}</p>
          <div className="overflow-x-auto max-h-96 overflow-y-auto border border-gray-200 rounded-md">
            <Table className="min-w-full divide-y divide-gray-200">
              <TableHeader className="bg-gray-50 sticky top-0">
                <TableRow>
                  {Object.keys(filteredClaim).map((header) => (
                    <TableHead key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{header}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody className="bg-white divide-y divide-gray-200">
                <TableRow className="hover:bg-gray-50 transition-colors">
                  {Object.values(filteredClaim).map((value, i) => (
                    <Popover key={i}>
                      <PopoverTrigger asChild>
                        <TableCell className="px-6 py-4 text-sm text-gray-900 whitespace-nowrap truncate max-w-[200px] cursor-pointer">{value}</TableCell>
                      </PopoverTrigger>
                      <PopoverContent className="max-w-md max-h-60 overflow-y-auto whitespace-pre-wrap break-words bg-white p-4 shadow-lg border border-gray-200 rounded-md">
                        {value}
                      </PopoverContent>
                    </Popover>
                  ))}
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-600 mb-6">Click on a category card to view details.</p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        {Object.entries(claimTypeMap).map(([key, { label, data }]) => (
          <Card 
            key={key} 
            className={`shadow-sm cursor-pointer transition-shadow ${selectedClaimType === key ? 'ring-2 ring-[#FB4E0B] shadow-md' : 'hover:shadow-md'}`}
            onClick={() => handleClaimTypeClick(key)}
          >
            <CardContent className="p-4">
              <p className="text-sm font-medium text-gray-600">{label}</p>
              <p className="text-2xl font-bold text-gray-900">{data.total_count}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      {selectedClaimType && (
        <div className="mb-6">
          <h4 className="text-md font-semibold text-gray-800 mb-4">{claimTypeMap[selectedClaimType].label} Claims</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            {Object.entries(validityMap).map(([validKey, { label, color }]) => (
              <Card 
                key={validKey} 
                className={`shadow-sm cursor-pointer transition-shadow ${selectedValidity === validKey ? 'ring-2 ring-[#FB4E0B] shadow-md' : 'hover:shadow-md'}`}
                onClick={() => handleValidityClick(validKey)}
              >
                <CardContent className="p-4">
                  <p className="text-sm font-medium text-gray-600">{label}</p>
                  <p className={`text-2xl font-bold ${color}`}>{claimTypeMap[selectedClaimType].data[validKey].count}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          {selectedValidity && (
            <>
              <div className="overflow-x-auto max-h-96 overflow-y-auto border border-gray-200 rounded-md">
                {(() => {
                  const fullData = claimTypeMap[selectedClaimType].data[selectedValidity].data;
                  const paginatedData = getPaginatedData(fullData);
                  const headers = fullData[0] ? Object.keys(fullData[0]) : [];
                  return (
                    <>
                      <Table className="min-w-full divide-y divide-gray-200">
                        <TableHeader className="bg-gray-50 sticky top-0">
                          <TableRow>
                            {!isHumanReview && (
                              <TableHead className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">Select</TableHead>
                            )}
                            {headers.map((header) => (
                              <TableHead key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">{header}</TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody className="bg-white divide-y divide-gray-200">
                          {paginatedData.map((row, idx) => {
                            const globalIdx = (currentPage - 1) * pageSize + idx;
                            return (
                              <TableRow key={globalIdx} className="hover:bg-gray-50 transition-colors">
                                {!isHumanReview && (
                                  <TableCell className="px-6 py-4 whitespace-nowrap">
                                    <Checkbox checked={selectedIndices.includes(globalIdx)} onCheckedChange={() => toggleSelect(globalIdx)} />
                                  </TableCell>
                                )}
                                {Object.values(row).map((value, i) => (
                                  <Popover key={i}>
                                    <PopoverTrigger asChild>
                                      <TableCell className="px-6 py-4 text-sm text-gray-900 whitespace-nowrap truncate max-w-[200px] cursor-pointer">{value}</TableCell>
                                    </PopoverTrigger>
                                    <PopoverContent className="max-w-md max-h-60 overflow-y-auto whitespace-pre-wrap break-words bg-white p-4 shadow-lg border border-gray-200 rounded-md">
                                      {value}
                                    </PopoverContent>
                                  </Popover>
                                ))}
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                      {fullData.length === 0 && (
                        <p className="text-gray-600 text-center mt-4">No data available for this subcategory.</p>
                      )}
                    </>
                  );
                })()}
              </div>
              <div className="mt-4 flex justify-between items-center">
                <div>
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {totalPages(claimTypeMap[selectedClaimType].data[selectedValidity].data.length)}
                  </span>
                </div>
                <div className="space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages(claimTypeMap[selectedClaimType].data[selectedValidity].data.length)}
                  >
                    Next
                  </Button>
                </div>
              </div>
              {!isHumanReview && (
                <div className="mt-4 text-left">
                  <Button 
                    onClick={handleAdd} 
                    disabled={selectedIndices.length === 0}
                    className="bg-[#FB4E0B] hover:bg-[#D93E0A] text-white"
                  >
                    {selectedIndices.length > 0 ? buttonText : 'Add Selected Row to Human Review'}
                  </Button>
                  {showConfirmation && (
                    <Alert variant="success" className="mt-4 border-green-500 max-w-md">
                      <AlertDescription>Claims added for human review</AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}