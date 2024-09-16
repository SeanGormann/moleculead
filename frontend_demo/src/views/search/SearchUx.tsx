import React from "react";
import {
  VuiFlexContainer,
  VuiFlexItem,
  VuiTitle,
  VuiSpinner,
  VuiSpacer,
} from "../../ui";
import { useSearchContext } from "../../contexts/SearchContext";
import { SearchResultList } from "./results/SearchResultList";
import { SearchErrorCallout } from "./results/SearchErrorCallout";

export const SearchUx = () => {
  const {
    isSearching,
    searchError,
    searchResults,
    searchResultsRef,
    selectedSearchResultPosition,
  } = useSearchContext();

  let content;

  console.log("Entering SearchUx:", { isSearching, searchError, searchResults, searchResultsRef, selectedSearchResultPosition });

  if (isSearching) {
    console.log("SearchUx: Currently searching...");
    content = (
      <VuiFlexContainer alignItems="center" spacing="m">
        <VuiFlexItem>
          <VuiSpinner size="s" />
        </VuiFlexItem>

        <VuiFlexItem grow={false}>
          <VuiTitle size="s" align="center">
            <h2>Searching</h2>
          </VuiTitle>
        </VuiFlexItem>
      </VuiFlexContainer>
    );
  } else if (searchError) {
    console.log("SearchUx: Search error encountered", searchError);
    content = <SearchErrorCallout searchError={searchError} />;
  } else if (searchResults?.length) {
    console.log("SearchUx: Displaying search results", searchResults);
    content = (
      <SearchResultList
        results={searchResults}
        selectedSearchResultPosition={selectedSearchResultPosition}
        setSearchResultRef={(el: HTMLDivElement | null, index: number) =>
          (searchResultsRef.current[index] = el)
        }
      />
    );
  } else {
    console.log("SearchUx: No search results to display");
    content = <VuiTitle size="s" align="center"><h2>No Results Found</h2></VuiTitle>;
  }

  return (
    <>
      <VuiSpacer size="m" />
      {content}
    </>
  );
};



