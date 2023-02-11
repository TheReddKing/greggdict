import React, { useState, useEffect, useMemo } from "react";

import SearchContainer from "./SearchContainer";
import ImageContainer from "./ImageContainer";
import Header from "./Header";
import Divider from "./Divider";
import FAQ from "./FAQ";
import Footer from "./Footer";
import GithubCorner from "./GithubCorner";
import { series } from "../settings";
import MultiWordContainer from "./MultiWordContainer";

const DEFAULT_SERIES_KEY = "gregg_dict01_default_series";

const App = () => {
  // current word the user has selected to look up in the dictionary
  const [word, setWord] = useState(null);
  const [words, setWords] = useState([]);

  // load stored series for user convenience
  let stored = localStorage.getItem(DEFAULT_SERIES_KEY);
  let defaultSeries = "";
  if (stored && series.includes(stored)) {
    defaultSeries = stored;
  } else {
    defaultSeries = series[0];
  }
  const [curSeries, setSeries] = useState(defaultSeries);

  function changeSeries(s) {
    // reset word when the series changes
    setSeries(s);
    setWord(null);

    // also save it to localStorage for convenience
    localStorage.setItem(DEFAULT_SERIES_KEY, s);
  }

  const wordContainers = useMemo(() => {
    return words.map((word, i) => {
      return (
        <div key={i}>
          <ImageContainer ismulti={true} word={word} series={curSeries} />
        </div>
      );
    });
  }, [words]);

  return (
    <div>
      <div className="font-sans max-w-xl mx-auto pt-1 px-2 sm:px-3">
        <GithubCorner />
        <Header />
        <SearchContainer
          onSelectWord={setWord}
          seriesList={series}
          curSeries={curSeries}
          setSeries={changeSeries}
        />
        <ImageContainer ismulti={false} word={word} series={curSeries} />
        <Divider />
      </div>
      <div className="font-sans mx-auto pt-1 px-5 sm:px-3">
        <h1>Multiwords</h1>
        <MultiWordContainer
          onSelectedWords={setWords}
          seriesList={series}
          curSeries={curSeries}
          setSeries={changeSeries}
        />
        <div style={{ display: "flex", flexWrap: "wrap" }}>
          {wordContainers}
        </div>
      </div>
      <div className="font-sans max-w-xl mx-auto pt-1 px-2 sm:px-3">
        <FAQ />
        <Footer />
      </div>
    </div>
  );
};

export default App;
