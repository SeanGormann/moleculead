import React from 'react';
import { ApiResponse } from './types';
import { extractSearchData } from '../../contexts/processApiResponse';
import SearchResultList from './SearchResultList';
import SummaryComponent from './SummaryComponent';

interface SearchComponentProps {
    apiResponse: ApiResponse;
}


const SearchComponent: React.FC<SearchComponentProps> = ({ apiResponse }) => {
    const data = extractSearchData(apiResponse); // directly assign without useState

    return (
        <div>
            <SummaryComponent question={data.question} response={data.response} />
            <SearchResultList rawDocuments={data.rawDocuments} />
        </div>
    );
};

export default SearchComponent;
