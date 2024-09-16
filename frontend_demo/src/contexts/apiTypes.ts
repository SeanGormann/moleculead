export interface ApiResponse {
    output: Output;
    callback_events: any[];
    metadata: Metadata;
  }
  
  export interface Output {
    question: string;
    reponse: string; // Note the typo here if it's from the API.
    raw_documents: RawDocument[];
  }
  
  export interface RawDocument {
    id: string;
    metadata: {
      title: string;
      url?: string;
      source?: string;
    };
    page_content?: string;
    type: string;
  }
  
  export interface Metadata {
    run_id: string;
  }
  
  export interface ProcessedSearchData {
    question: string;
    response: string;
    rawDocuments: RawDocument[];
    metadata: Metadata;
  }
  