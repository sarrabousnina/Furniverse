import React, { useState } from 'react';
import { searchWithTradeoffs } from '../../services/api';
import { useProducts } from '../../context/ProductsContext';
import ProductCard from '../ProductCard/ProductCard';
import TradeOffCard from '../TradeOffCard/TradeOffCard';
import styles from './AISearchBar.module.css';

const AISearchBar = ({ onResultsFound }) => {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const { products } = useProducts();

  const exampleQueries = [
    "Comfy blue sofa under 500",
    "Leather couch for my living room",
    "Modern dining table under 800",
    "Velvet chair for bedroom",
    "Storage bed with budget of 1000"
  ];

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setResults(null);

    try {
      // Use trade-off search instead of smart search
      const response = await searchWithTradeoffs(query);

      console.log('Trade-off Search Results:', response);

      // Helper function to match products
      const matchProduct = (p) => {
        let fullProduct = products.find(prod =>
          prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
          p.name.toLowerCase().includes(prod.name.toLowerCase())
        );

        if (!fullProduct) {
          const searchWords = p.name.toLowerCase().split(' ').slice(0, 3).join(' ');
          fullProduct = products.find(prod =>
            prod.name.toLowerCase().includes(searchWords) ||
            searchWords.includes(prod.name.toLowerCase())
          );
        }

        return fullProduct;
      };

      // Process exact matches
      const exactMatchesWithDetails = (response.exact_matches || []).map(p => {
        const fullProduct = matchProduct(p);
        return {
          ...p,
          fullProduct: fullProduct || null
        };
      }).filter(p => p.fullProduct !== null);

      // Process trade-offs
      const tradeOffsWithDetails = (response.trade_offs || []).map(p => {
        const fullProduct = matchProduct(p);
        return {
          ...p,
          fullProduct: fullProduct || null
        };
      }).filter(p => p.fullProduct !== null);

      console.log('Exact matches:', exactMatchesWithDetails.length);
      console.log('Trade-offs:', tradeOffsWithDetails.length);

      setResults({
        ...response,
        exact_matches: exactMatchesWithDetails,
        trade_offs: tradeOffsWithDetails
      });

      if (onResultsFound) {
        const allResults = [...exactMatchesWithDetails, ...tradeOffsWithDetails];
        onResultsFound(allResults);
      }
    } catch (err) {
      setError('Failed to search. Please try again.');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    // Trigger search automatically using trade-off search
    setTimeout(() => {
      searchWithTradeoffs(exampleQuery)
        .then(response => {
          // Helper function to match products
          const matchProduct = (p) => {
            let fullProduct = products.find(prod =>
              prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
              p.name.toLowerCase().includes(prod.name.toLowerCase())
            );

            if (!fullProduct) {
              const searchWords = p.name.toLowerCase().split(' ').slice(0, 3).join(' ');
              fullProduct = products.find(prod =>
                prod.name.toLowerCase().includes(searchWords) ||
                searchWords.includes(prod.name.toLowerCase())
              );
            }

            return fullProduct;
          };

          // Process exact matches
          const exactMatchesWithDetails = (response.exact_matches || []).map(p => {
            const fullProduct = matchProduct(p);
            return {
              ...p,
              fullProduct: fullProduct || null
            };
          }).filter(p => p.fullProduct !== null);

          // Process trade-offs
          const tradeOffsWithDetails = (response.trade_offs || []).map(p => {
            const fullProduct = matchProduct(p);
            return {
              ...p,
              fullProduct: fullProduct || null
            };
          }).filter(p => p.fullProduct !== null);

          setResults({
            ...response,
            exact_matches: exactMatchesWithDetails,
            trade_offs: tradeOffsWithDetails
          });

          if (onResultsFound) {
            const allResults = [...exactMatchesWithDetails, ...tradeOffsWithDetails];
            onResultsFound(allResults);
          }
        })
        .catch(err => {
          setError('Failed to search. Please try again.');
          console.error('Search error:', err);
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
          <svg className={styles.searchIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
              <>
               
                Search
              </>
            )}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className={styles.errorMessage}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
              </svg>
              Trade-off Analysis
            </h3>

            <div className={styles.analysisContent}>
              <div className={styles.analysisItem}>
                <span className={styles.analysisLabel}>Query:</span>
                <span className={styles.analysisValue}>"{results.query}"</span>
              </div>

              {results.user_preferences && (
                <>
                  {results.user_preferences.budget && (
                    <div className={styles.analysisItem}>
                      <span className={styles.analysisLabel}>💰 Budget:</span>
                      <span className={styles.analysisValue}>Under ${results.user_preferences.budget}</span>
                    </div>
                  )}
                  {results.user_preferences.material && (
                    <div className={styles.analysisItem}>
                      <span className={styles.analysisLabel}>🎨 Material:</span>
                      <span className={styles.analysisValue}>{results.user_preferences.material}</span>
                    </div>
                  )}
                  {results.user_preferences.style && (
                    <div className={styles.analysisItem}>
                      <span className={styles.analysisLabel}>✨ Style:</span>
                      <span className={styles.analysisValue}>{results.user_preferences.style}</span>
                    </div>
                  )}
                  {results.user_preferences.color && (
                    <div className={styles.analysisItem}>
                      <span className={styles.analysisLabel}>🎨 Color:</span>
                      <span className={styles.analysisValue}>{results.user_preferences.color}</span>
                    </div>
                  )}
                </>
              )}

              {results.explanation && (
                <div className={styles.explanation}>
                  <p>{results.explanation}</p>
                </div>
              )}

              <div className={styles.summaryStats}>
                <div className={styles.stat}>
                  <span className={styles.statValue}>{results.exact_matches?.length || 0}</span>
                  <span className={styles.statLabel}>Perfect Matches</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statValue}>{results.trade_offs?.length || 0}</span>
                  <span className={styles.statLabel}>Smart Alternatives</span>
                </div>
              </div>
            </div>
          </div>

          {/* Exact Matches Section */}
          {results.exact_matches && results.exact_matches.length > 0 && (
            <div className={styles.resultsSection}>
              <h4 className={styles.sectionTitle}>✅ Perfect Matches</h4>
              <div className={styles.productsGrid}>
                {results.exact_matches.map((item) => (
                  <ProductCard
                    key={item.product_id}
                    product={item.fullProduct}
                    score={item.score}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Trade-offs Section */}
          {results.trade_offs && results.trade_offs.length > 0 && (
            <div className={styles.resultsSection}>
              <h4 className={styles.sectionTitle}>💡 Smart Alternatives (Trade-offs Analyzed)</h4>
              <div className={styles.tradeOffsGrid}>
                {results.trade_offs.map((item) => (
                  <TradeOffCard
                    key={item.product_id}
                    product={{
                      ...item,
                      ...item.fullProduct
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {((!results.exact_matches || results.exact_matches.length === 0) &&
            (!results.trade_offs || results.trade_offs.length === 0)) && (
            <div className={styles.noResults}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
