/*
import axios from "axios";
import { START_TAG, END_TAG } from "../utils/parseSnippet";
import { SummaryLanguage, mmr_reranker_id } from "../views/search/types";

type Config = {
  filter: string;
  query_str?: string;
  language?: SummaryLanguage;
  summaryMode?: boolean;
  rerank?: boolean;
  rerankNumResults?: number;
  rerankerId?: number;
  rerankDiversityBias?: number;
  hybridNumWords: number;
  hybridLambdaShort?: number;
  hybridLambdaLong?: number;
  mode?: string;
  summaryNumResults?: number;
  summaryNumSentences?: number;
  summaryPromptName?: string;
  summaryPromptText?: string;
  enableFactualConsistencyScore?: boolean
  customerId: string;
  corpusId: string;
  endpoint: string;
  apiKey: string;
  logQuery?: boolean;
};

export const sendSearchRequest = async ({
  filter,
  query_str,
  language,
  summaryMode,
  rerank,
  rerankNumResults,
  rerankerId,
  rerankDiversityBias,
  hybridNumWords,
  hybridLambdaShort,
  hybridLambdaLong,
  mode,
  summaryNumResults,
  summaryNumSentences,
  summaryPromptName,
  summaryPromptText,
  enableFactualConsistencyScore,
  customerId,
  corpusId,
  endpoint,
  apiKey,
  logQuery=false
}: Config) => {
  const lambda =
    typeof query_str === "undefined" || query_str.trim().split(" ").length > hybridNumWords
      ? hybridLambdaLong
      : hybridLambdaShort;
  const corpusKeyList = corpusId.split(",").map((id) => {
    return {
      customerId,
      corpusId: id,
      lexicalInterpolationConfig: {
        lambda: lambda,
      },
      metadataFilter: filter ? `doc.source = '${filter}'` : undefined,
      semantics: mode ? `RESPONSE` : undefined,
    };
  });

  if (summaryPromptText) {
    summaryPromptText = summaryPromptText.replaceAll("\\n", "\n");
    summaryPromptText = summaryPromptText.replaceAll("\\\"", "\\\\\\\"");
  }

  const body = {
    logQuery: logQuery, // passing request middleware to decide log the query or not
    query: [
      {
        query: query_str,
        start: 0,
        numResults: rerank ? rerankNumResults : 10,
        corpusKey: corpusKeyList,
        contextConfig: {
          sentencesBefore: summaryMode ? summaryNumSentences : 2,
          sentencesAfter: summaryMode ? summaryNumSentences : 2,
          startTag: START_TAG,
          endTag: END_TAG,
        },
        ...(summaryMode
          ? {
              summary: [
                {
                  responseLang: language,
                  maxSummarizedResults: summaryNumResults,
                  summarizerPromptName: summaryPromptName,
                  promptText: summaryPromptText,
                  factualConsistencyScore: enableFactualConsistencyScore ?? false
                },
              ],
            }
          : {}),
        ...(rerank
          ? {
              rerankingConfig: {
                rerankerId: rerankerId,
                ...(rerankerId === mmr_reranker_id ? {
                      mmrConfig: {
                        diversityBias: rerankDiversityBias,
                      }
                    } : {}
                ),
              },
            }
          : {}),
      },
    ],
  };

  let headers = {};
  let url = "";
  if (process.env.NODE_ENV === "production") {
    // Call proxy server if in production
    url = `/v1/query`;
    headers = {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    };
  } else {
    // Call directly if in development
    url = `https://${endpoint}/v1/query`;
    headers = {
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "customer-id": customerId,
        "x-api-key": apiKey,
        "grpc-timeout": "60S",
      },
    };
  }

  // Log the request details
  console.log("Sending API Request to:", url, "with body:", body, "and headers:", headers);

  // Perform the API request
  const result = await axios.post(url, body, headers);

  // Log the received response
  console.log("Received API Response:", result.data);

  console.log("Received API Response Set:", result.data.responseSet);
  console.log("Received API Response Set 0:", result.data.responseSet[0]);

  return result.data.responseSet[0]; // You may adjust based on actual API response structure
};
*/



import axios from "axios";
//import { START_TAG, END_TAG } from "../utils/parseSnippet";
import { SummaryLanguage } from "../views/search/types"; //mmr_reranker_id

type Config = {
  filter: string;
  query_str?: string;
  language?: SummaryLanguage;
  summaryMode?: boolean;
  rerank?: boolean;
  rerankNumResults?: number;
  rerankerId?: number;
  rerankDiversityBias?: number;
  hybridNumWords: number;
  hybridLambdaShort?: number;
  hybridLambdaLong?: number;
  mode?: string;
  summaryNumResults?: number;
  summaryNumSentences?: number;
  summaryPromptName?: string;
  summaryPromptText?: string;
  enableFactualConsistencyScore?: boolean
  customerId: string;
  corpusId: string;
  endpoint: string;
  apiKey: string;
  logQuery?: boolean;
};


export const sendSearchRequest = async ({
  query_str,
  endpoint,
  apiKey
}: Config) => {

  const body = {
    input: {  // Encapsulate the query inside 'input'
      query: query_str
    }
  };

  let headers = {};
  let url = "";

  if (process.env.NODE_ENV === "production") {
    // Call proxy server if in production
    url = `/my_chain/invoke`;  // Updated to use your specific local server route
    headers = {
      headers: {
        "Content-Type": "application/json", // Adjust this to your server's expectations, usually would be application/json
        Accept: "application/json",
      },
    };
  } else {
    // Call directly if in development
    //url = `http://${endpoint}/my_chain/invoke`; // Updated to direct local endpoint
    url = `http://127.0.0.1:8000/my_chain/invoke`; // Updated to direct local endpoint
    headers = {
      headers: {
        "Content-Type": "application/json", // Same note as above regarding the content type
        Accept: "application/json",
        //"customer-id": apiKey, // Assuming apiKey is used as customer-id, adjust accordingly
      },
    };
  }

  // Log the request details
  console.log("Sending API Request to:", url, "with body:", body, "and headers:", headers);

  // Perform the API request
  const result = await axios.post(url, body, headers);

  // Log the received response
  console.log("Received API Response:", result.data);

  // Check if the output exists and return it, adjust based on the actual API response structure
  if (result.data && result.data.output) {
    console.log("Detailed Output:", result.data);
    return result.data; // Return the 'output' part of the response
  } else {
    // Handle cases where output may not be present or errors occur
    console.error("No output in response or error occurred");
    return null;
  }
};



