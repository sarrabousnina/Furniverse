import React, { useState } from "react";
import { smartSearch } from "../../services/api";
import { useProducts } from "../../context/ProductsContext";
import ProductCard from "../ProductCard/ProductCard";
import styles from "./AISearchBar.module.css";

const AISearchBar = ({ onResultsFound }) => {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const { products } = useProducts();

  const exampleQueries = [
    "Comfy blue sofa under 500",
    "Leather couch for my living room",
    "Modern dining table under 800",
    "Velvet chair for bedroom",
    "Storage bed with budget of 1000",
  ];

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setResults(null);

    try {
      // Use smart search with our fixed backend
      const response = await smartSearch(query);

      console.log("AI Search Results:", response);

      // Helper function to match products by ID (most accurate)
      const matchProduct = (p) => {
        // Match by product_id first (most accurate for color variants)
        let fullProduct = products.find(
          (prod) => String(prod.id) === String(p.product_id),
        );

        // Fallback: match by name if ID not found (shouldn't happen)
        if (!fullProduct) {
          fullProduct = products.find(
            (prod) =>
              prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
              p.name.toLowerCase().includes(prod.name.toLowerCase()),
          );
        }

        console.log(
          `Matching ID ${p.product_id} "${p.name}" ->`,
          fullProduct ? `${fullProduct.id}: ${fullProduct.name}` : "NOT FOUND",
        );

        return fullProduct;
      };

      // Process products from smart search response
      const perfectMatchesWithDetails = (response.perfect_matches || [])
        .map((p) => {
          const fullProduct = matchProduct(p);
          return {
            ...p,
            fullProduct: fullProduct || null,
          };
        })
        .filter((p) => p.fullProduct !== null);

      // Process alternatives (wrong color/material but within budget)
      const alternativesWithDetails = (response.alternatives || [])
        .map((p) => {
          const fullProduct = matchProduct(p);
          return {
            ...p,
            fullProduct: fullProduct || null,
          };
        })
        .filter((p) => p.fullProduct !== null);

      // Process over-budget options (over budget with compromise analysis)
      const overBudgetWithDetails = (response.over_budget_options || [])
        .map((p) => {
          const fullProduct = matchProduct(p);
          return {
            ...p,
            fullProduct: fullProduct || null,
          };
        })
        .filter((p) => p.fullProduct !== null);

      console.log("Perfect matches:", perfectMatchesWithDetails.length);
      console.log("Alternatives:", alternativesWithDetails.length);
      console.log("Over-budget options:", overBudgetWithDetails.length);

      setResults({
        ...response,
        perfect_matches: perfectMatchesWithDetails,
        alternatives: alternativesWithDetails,
        over_budget_options: overBudgetWithDetails,
      });

      if (onResultsFound) {
        const allResults = [
          ...perfectMatchesWithDetails,
          ...alternativesWithDetails,
          ...overBudgetWithDetails,
        ];
        onResultsFound(allResults);
      }
    } catch (err) {
      setError("Failed to search. Please try again.");
      console.error("Search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    // Trigger search automatically using trade-off search
    setTimeout(() => {
      searchWithTradeoffs(exampleQuery)
        .then((response) => {
          // Helper function to match products by ID (most accurate)
          const matchProduct = (p) => {
            // Match by product_id first (most accurate for color variants)
            let fullProduct = products.find(
              (prod) => String(prod.id) === String(p.product_id),
            );

            // Fallback: match by name if ID not found (shouldn't happen)
            if (!fullProduct) {
              fullProduct = products.find(
                (prod) =>
                  prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
                  p.name.toLowerCase().includes(prod.name.toLowerCase()),
              );
            }

            return fullProduct;
          };

          // Process products from smart search response
          const perfectMatchesWithDetails = (response.perfect_matches || [])
            .map((p) => {
              const fullProduct = matchProduct(p);
              return {
                ...p,
                fullProduct: fullProduct || null,
              };
            })
            .filter((p) => p.fullProduct !== null);

          const alternativesWithDetails = (response.alternatives || [])
            .map((p) => {
              const fullProduct = matchProduct(p);
              return {
                ...p,
                fullProduct: fullProduct || null,
              };
            })
            .filter((p) => p.fullProduct !== null);

          const overBudgetWithDetails = (response.over_budget_options || [])
            .map((p) => {
              const fullProduct = matchProduct(p);
              return {
                ...p,
                fullProduct: fullProduct || null,
              };
            })
            .filter((p) => p.fullProduct !== null);

          setResults({
            ...response,
            perfect_matches: perfectMatchesWithDetails,
            alternatives: alternativesWithDetails,
            over_budget_options: overBudgetWithDetails,
          });

          if (onResultsFound) {
            const allResults = [
              ...perfectMatchesWithDetails,
              ...alternativesWithDetails,
              ...overBudgetWithDetails,
            ];
            onResultsFound(allResults);
          }
        })
        .catch((err) => {
          setError("Failed to search. Please try again.");
          console.error("Search error:", err);
        })
        .finally(() => {
          setIsSearching(false);
        });
    }, 100);
  };

  return (
    <div className={styles.aiSearchSection}>
      {/* Search Form */}
      <form onSubmit={handleSearch} className={styles.searchForm}>
        <div className={styles.inputWrapper}>
          <svg
            className={styles.searchIcon}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'Comfy blue sofa under 500' or 'Leather couch for my living room'"
            className={styles.searchInput}
            disabled={isSearching}
          />
          <button
            type="submit"
            className={styles.searchButton}
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? (
              <>
                <span className={styles.spinner}></span>
                Searching...
              </>
            ) : (
              <>Search</>
            )}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className={styles.errorMessage}>
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error}
        </div>
      )}

      {/* Examples */}
      {!results && !error && (
        <div className={styles.examplesSection}>
          <p className={styles.examplesLabel}>💡 Try these examples:</p>
          <div className={styles.examplesList}>
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                type="button"
                className={styles.exampleButton}
                onClick={() => handleExampleClick(example)}
              >
                "{example}"
              </button>
            ))}
          </div>
        </div>
      )}

      {/* AI Analysis & Results */}
      {results && (
        <div className={styles.resultsSection}>
          {/* AI Analysis */}
          <div className={styles.aiAnalysis}>
            <h3 className={styles.analysisTitle}>
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
              AI Analysis
            </h3>

            <div className={styles.analysisContent}>
              <div className={styles.analysisItem}>
                <span className={styles.analysisLabel}>Query:</span>
                <span className={styles.analysisValue}>"{results.query}"</span>
              </div>

              {results.user_requirements?.budget && (
                <div className={styles.analysisItem}>
                  <span className={styles.analysisLabel}>💰 Budget:</span>
                  <span className={styles.analysisValue}>
                    Under ${results.user_requirements.budget}
                  </span>
                </div>
              )}

              <div className={styles.analysisItem}>
                <span className={styles.analysisLabel}>🎯 Strategy:</span>
                <span className={styles.analysisValue}>
                  Compromise Analysis
                </span>
              </div>

              {results.explanation && (
                <div className={styles.explanation}>
                  <p>{results.explanation}</p>
                </div>
              )}
            </div>
          </div>

          {/* Products Grid */}
          {results.perfect_matches && results.perfect_matches.length > 0 && (
            <>
              <h4 className={styles.sectionTitle}>✅ Perfect Matches</h4>
              <p className={styles.sectionDescription}>
                Within budget and matches your color/material requirements
              </p>
              <div className={styles.productsGrid}>
                {results.perfect_matches.map((item) => (
                  <div
                    key={item.product_id}
                    className={styles.productCardWrapper}
                  >
                    <ProductCard
                      product={item.fullProduct}
                      score={item.score}
                    />
                    {item.compromise && item.compromise.summary && (
                      <div className={styles.compromiseBadge}>
                        <span className={styles.compromiseIcon}>✨</span>
                        <span className={styles.compromiseText}>
                          {item.compromise.summary}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Alternatives (different color/material but within budget) */}
          {results.alternatives && results.alternatives.length > 0 && (
            <>
              <h4 className={styles.sectionTitle}>
                🎨 Alternatives (Different Color/Material)
              </h4>
              <p className={styles.sectionDescription}>
                High similarity but different color or material - still within
                budget
              </p>
              <div className={styles.productsGrid}>
                {results.alternatives.map((item) => (
                  <div key={item.product_id} className={styles.tradeoffCard}>
                    <ProductCard
                      product={item.fullProduct}
                      score={item.score}
                    />
                    {item.compromise && (
                      <div className={styles.compromiseAnalysis}>
                        <div className={styles.compromiseSummary}>
                          📝 {item.compromise.summary}
                        </div>
                        {item.compromise.advantages &&
                          item.compromise.advantages.length > 0 && (
                            <div className={styles.advantagesList}>
                              <span className={styles.advantagesTitle}>
                                ✨ Advantages:
                              </span>
                              <ul>
                                {item.compromise.advantages.map((adv, idx) => (
                                  <li key={idx}>{adv}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        {item.compromise.disadvantages &&
                          item.compromise.disadvantages.length > 0 && (
                            <div className={styles.disadvantagesList}>
                              <span className={styles.disadvantagesTitle}>
                                ⚠️ Trade-offs:
                              </span>
                              <ul>
                                {item.compromise.disadvantages.map(
                                  (dis, idx) => (
                                    <li key={idx}>{dis}</li>
                                  ),
                                )}
                              </ul>
                            </div>
                          )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Over Budget Options with Compromise Analysis */}
          {results.over_budget_options &&
            results.over_budget_options.length > 0 && (
              <>
                <h4 className={styles.sectionTitle}>
                  💰 Over-Budget Options (Worth Considering)
                </h4>
                <p className={styles.sectionDescription}>
                  High-quality matches that cost more - see their advantages and
                  disadvantages
                </p>
                <div className={styles.productsGrid}>
                  {results.over_budget_options.map((item) => (
                    <div key={item.product_id} className={styles.tradeoffCard}>
                      <ProductCard
                        product={item.fullProduct}
                        score={item.score}
                      />
                      {item.compromise && (
                        <div className={styles.compromiseAnalysis}>
                          <div className={styles.compromiseSummary}>
                            📝 {item.compromise.summary}
                          </div>
                          {item.compromise.advantages &&
                            item.compromise.advantages.length > 0 && (
                              <div className={styles.advantagesList}>
                                <span className={styles.advantagesTitle}>
                                  ✨ Advantages:
                                </span>
                                <ul>
                                  {item.compromise.advantages.map(
                                    (adv, idx) => (
                                      <li key={idx}>{adv}</li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}
                          {item.compromise.disadvantages &&
                            item.compromise.disadvantages.length > 0 && (
                              <div className={styles.disadvantagesList}>
                                <span className={styles.disadvantagesTitle}>
                                  ⚠️ Disadvantages:
                                </span>
                                <ul>
                                  {item.compromise.disadvantages.map(
                                    (dis, idx) => (
                                      <li key={idx}>{dis}</li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </>
            )}

          {results.perfect_matches &&
            results.perfect_matches.length === 0 &&
            (!results.alternatives || results.alternatives.length === 0) &&
            (!results.over_budget_options ||
              results.over_budget_options.length === 0) && (
              <div className={styles.noResults}>
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <p>No products found matching your criteria.</p>
                <p>Try adjusting your budget or search terms.</p>
              </div>
            )}
        </div>
      )}
    </div>
  );
};

export default AISearchBar;
