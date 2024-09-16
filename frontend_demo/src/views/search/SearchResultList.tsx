import React from 'react';
import { RawDocument } from './types'; // Adjust the path as necessary

interface SearchResultListProps {
    rawDocuments: RawDocument[];
}

const SearchResultList: React.FC<SearchResultListProps> = ({ rawDocuments }) => {
    return (
        <ul>
            {rawDocuments.map((doc, index) => (
                <li key={index}>
                    Document ID: {doc.id}, Title: {doc.metadata?.title}
                </li>
            ))}
        </ul>
    );
};

export default SearchResultList;

