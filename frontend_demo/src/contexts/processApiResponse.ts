import { ApiResponse, ProcessedSearchData } from './apiTypes';

export function extractSearchData(apiResponse: ApiResponse): ProcessedSearchData {
    const { output, metadata } = apiResponse;

    return {
        question: output.question || "",
        response: output.reponse || "", // Mind the typo 'reponse'
        rawDocuments: output.raw_documents || [],
        metadata
    };
}
