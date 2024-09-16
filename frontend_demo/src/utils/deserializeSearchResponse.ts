import { parseSnippet } from "./parseSnippet";
import { DeserializedSearchResult } from "../views/search/types";


type metaMetadata = {
  source: string;
  title: string;
  url: string;
};

interface RawDocument {
  id: string;
  page_content: string;
  metadata: metaMetadata; // Array<metaMetadata>;  // Define more specifically if possible
}

interface myApiResponse {
  callback_events: Array<any>;
  metadata: {
    run_id: string;
  };
  output: {
    question: string;
    reponse: string;  // Note the typo here if it's from the API.
    raw_documents: RawDocument[];
  };

}



export const deserializeSearchResponse = (
  myApiResponse: myApiResponse | undefined
): Array<DeserializedSearchResult> | undefined => {
  if (!myApiResponse?.output) return undefined;

  const results: Array<DeserializedSearchResult> = [];

  //console.log("myApiResponse in deserialiser:", myApiResponse);

  if (myApiResponse.output.raw_documents) {
      myApiResponse.output.raw_documents.forEach((document:RawDocument) => {
      const { pre, post } = parseSnippet(document.page_content);

      results.push({
        id: document.id,
        snippet: {
          pre,
          text: "", // Set text to an empty string
          post
        },
        source: document.metadata.source,
        url: document.metadata.url,
        title: document.metadata.title, //|| text.split(' ').slice(0, 10).join(' '),
        metadata: document.metadata,
      } as DeserializedSearchResult);
    });
  }
  return results;
};

