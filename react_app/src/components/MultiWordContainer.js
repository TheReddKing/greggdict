import React, { useEffect, useState, useMemo, useRef } from "react";

import Fuse from "fuse.js";

import SearchInput from "./SearchInput";
import { dictRoot } from "../settings";

const SEARCH_LIMIT = 50;

const MultiWordContainer = ({
  onSelectedWords,
  seriesList,
  curSeries,
  setSeries,
}) => {
  // list of words with the corresponding page number
  const [words, setWords] = useState([]);

  // cache reference dictionary to prevent unnecessary requests
  const cached = useRef({});

  // get the reference dictionary for the series
  useEffect(() => {
    if (cached.current[curSeries]) {
      const words = {};

      for (const val of cached.current[curSeries]) {
        words[val.t] = val;
      }
      setWords(words);
    }

    const xhr = new XMLHttpRequest();

    // Setup our listener to process compeleted requests
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== 4) return;

      if (xhr.status === 200) {
        const reference = JSON.parse(xhr.responseText);
        let response = (reference || []).flatMap((p) =>
          p.words.map((w) => ({ ...w, page: p.page }))
        );
        cached.current[curSeries] = response;

        const words = {};
        for (const val of cached.current[curSeries]) {
          words[val.t] = val;
        }
        setWords(words);
      } else {
        // status of 0 if request was aborted
        if (xhr.status === 0) return;

        alert(
          `Could not get the dictionary for ${curSeries}. This error has been automatically reported`
        );
        throw new Error(
          `Could not get reference json for dictRoot: ${dictRoot} and series: ${curSeries}`
        );
      }
    };
    xhr.open("GET", `${dictRoot}/${curSeries}/reference.json`);
    xhr.send();

    return () => xhr.abort();
  }, [curSeries]);

  const [str, setStr] = useState("");

  function changeSeries(s) {
    setSeries(s);
    // reset word when changing series to get different suggestions
    setStr("");
  }

  useEffect(() => {
    if (str.length == 0) {
      onSelectedWords([]);
    } else {
      let mywords = str.toLowerCase().replace(".", "").split(" ");
      mywords = mywords.filter((word) => word.length > 0);
      mywords = mywords
        .map((word) => {
          if (words[word] != null) {
            return words[word];
          }
          let new_word = word.substring(0, word.length - 1);
          return words[new_word];
        })
        .filter((word) => word != null);

      onSelectedWords(mywords);
    }
  }, [str, words]);

  return (
    <div className="my-4 text-lg relative">
      <SearchInput
        value={str}
        onChange={setStr}
        series={seriesList}
        curSeries={curSeries}
        onChooseSeries={changeSeries}
      />
    </div>
  );
};

export default MultiWordContainer;
