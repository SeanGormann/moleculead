import { SearchResult } from "./SearchResult";
import { DeserializedSearchResult } from "../types";

type Props = {
  results: Array<DeserializedSearchResult>;
  selectedSearchResultPosition?: number;
  setSearchResultRef: (el: HTMLDivElement | null, index: number) => void;
};

export const SearchResultList = ({ results, selectedSearchResultPosition, setSearchResultRef }: Props) => {
  console.log("Rendering SearchResultList with results:", results);
  return (
    <>
      {results.length > 0 ? (
        results.map((result, i) => (
          <SearchResult
            key={i}
            result={result}
            position={i}
            isSelected={selectedSearchResultPosition === i}
            ref={(el: HTMLDivElement | null) => setSearchResultRef(el, i)}
          />
        ))
      ) : (
        <div>No results to display.</div>
      )}
    </>
  );
};

