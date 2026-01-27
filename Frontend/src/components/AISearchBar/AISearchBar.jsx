import React, { useState } from 'react';
import { smartSearch } from '../../services/api';
import { useProducts } from '../../context/ProductsContext';
import ProductCard from '../ProductCard/ProductCard';
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
      const response = await smartSearch(query);

      console.log('AI Search Results:', response.products);

      // Fetch full product details for each result by matching name
      const productsWithDetails = response.products.map(p => {
        // Try multiple matching strategies
        let fullProduct = products.find(prod =>
          prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
          p.name.toLowerCase().includes(prod.name.toLowerCase())
        );

        // If not found, try partial matching (first 3 words)
        if (!fullProduct) {
          const searchWords = p.name.toLowerCase().split(' ').slice(0, 3).join(' ');
          fullProduct = products.find(prod =>
            prod.name.toLowerCase().includes(searchWords) ||
            searchWords.includes(prod.name.toLowerCase())
          );
        }

        console.log(`Matching "${p.name}" ->`, fullProduct ? fullProduct.name : 'NOT FOUND');

        return {
          ...p,
          fullProduct: fullProduct || null
        };
      }).filter(p => p.fullProduct !== null);

      console.log('Final matched products:', productsWithDetails.map(p => p.fullProduct.name));

      setResults({
        ...response,
        products: productsWithDetails
      });

      if (onResultsFound) {
        onResultsFound(productsWithDetails);
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
    // Trigger search automatically
    setTimeout(() => {
      const syntheticEvent = { preventDefault: () => {} };
      smartSearch(exampleQuery)
        .then(response => {
          const productsWithDetails = response.products.map(p => {
            // Try to find product by name (case-insensitive)
            let fullProduct = products.find(prod =>
              prod.name.toLowerCase().includes(p.name.toLowerCase()) ||
              p.name.toLowerCase().includes(prod.name.toLowerCase())
            );

            // If not found, try partial matching (first 3 words)
            if (!fullProduct) {
              const searchWords = p.name.toLowerCase().split(' ').slice(0, 3).join(' ');
              fullProduct = products.find(prod =>
                prod.name.toLowerCase().includes(searchWords) ||
                searchWords.includes(prod.name.toLowerCase())
              );
            }

            return {
              ...p,
              fullProduct: fullProduct || null
            };
          }).filter(p => p.fullProduct !== null);

          setResults({
            ...response,
            products: productsWithDetails
          });

          if (onResultsFound) {
            onResultsFound(productsWithDetails);
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
              AI Analysis
            </h3>

            <div className={styles.analysisContent}>
              <div className={styles.analysisItem}>
                <span className={styles.analysisLabel}>Query:</span>
                <span className={styles.analysisValue}>"{results.query}"</span>
              </div>

              {results.budget_limit && (
                <div className={styles.analysisItem}>
                  <span className={styles.analysisLabel}>💰 Budget:</span>
                  <span className={styles.analysisValue}>Under {results.budget_limit} TND</span>
                </div>
              )}

              <div className={styles.analysisItem}>
                <span className={styles.analysisLabel}>🎯 Strategy:</span>
                <span className={styles.analysisValue}>
                  {results.strategy === 'graph_substitutes' ? 'Smart Substitutes' : 'Direct Match'}
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
          {results.products && results.products.length > 0 && (
            <>

              <div className={styles.productsGrid}>
                {results.products.map((item) => (
                  <ProductCard
                    key={item.product_id}
                    product={item.fullProduct}
                    score={item.score}
                  />
                ))}
              </div>
            </>
          )}

          {results.products && results.products.length === 0 && (
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
