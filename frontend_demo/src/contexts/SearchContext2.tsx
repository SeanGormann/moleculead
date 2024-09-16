import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ApiResponse } from '../views/search/types';

interface SearchContextState {
    apiResponse: ApiResponse | null;
    setApiResponse: React.Dispatch<React.SetStateAction<ApiResponse | null>>;
    isLoading: boolean;
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
}

const SearchContext = createContext<SearchContextState | undefined>(undefined);

interface SearchProviderProps {
    children: ReactNode;
}

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
    const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const value = {
        apiResponse,
        setApiResponse,
        isLoading,
        setIsLoading
    };

    return (
        <SearchContext.Provider value={value}>
            {children}
        </SearchContext.Provider>
    );
};

export const useSearch = () => {
    const context = useContext(SearchContext);
    if (!context) {
        throw new Error('useSearch must be used within a SearchProvider');
    }
    return context;
};
