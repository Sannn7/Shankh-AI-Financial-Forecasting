
import { useState, useRef, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import Nifty500 from "../lib/nifty500.json";
import Company5 from "../lib/top5.json";

import { NIFTY_500_COMPANIES, StockSearchResult } from '@/api/stockApi';
import { cn } from '@/lib/utils';

interface SearchableDropdownProps {
  onSelect: (ticker: string) => void;
  className?: string;
}

export default function SearchableDropdown({ onSelect, className }: SearchableDropdownProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (query.length > 0) {
      const filtered = Company5.filter(
        (company) =>
          company.name.toLowerCase().includes(query.toLowerCase()) ||
          company.ticker.toLowerCase().includes(query.toLowerCase())
      );
      setResults(filtered);
    } else {
      setResults([]);
    }
  }, [query]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
  };

  const handleSelect = (ticker: string) => {
    setQuery('');
    setIsOpen(false);
    onSelect(ticker);
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
  };

  return (
    <div className={cn("relative w-full", className)} ref={dropdownRef}>
      <div className="relative flex items-center">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          value={query}
          onChange={handleSearch}
          onFocus={() => setIsOpen(true)}
          placeholder="Search for a stock (e.g., RELIANCE, HDFC)"
          className="w-full rounded-lg border border-input bg-background py-3 pl-10 pr-10 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-border bg-popover shadow-md glass-dark dark:glass-dark glass-light light:glass-light animate-fade-in">
          <ul className="py-1">
            {results.map((result) => (
              <li
                key={result.ticker}
                onClick={() => handleSelect(result.ticker)}
                className="cursor-pointer px-4 py-2 hover:bg-muted transition-colors"
              >
                <div className="flex justify-between">
                  <span className="font-medium">{result.name}</span>
                  <span className="text-muted-foreground">{result.ticker}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
