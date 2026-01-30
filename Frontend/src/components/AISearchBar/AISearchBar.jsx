import React, { useState, useRef } from "react";
import { smartSearch, searchByImage } from "../../services/api";
import { useProducts } from "../../context/ProductsContext";
import ProductCard from "../ProductCard/ProductCard";
import styles from "./AISearchBar.module.css";

const AISearchBar = ({ onResultsFound }) => {
  const [query, setQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [searchMode, setSearchMode] = useState("text"); // "text" or "image"
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);
  const { products } = useProducts();

  const exampleQueries = [
    "Comfy blue sofa under 500",
    "Leather couch for my living room",
    "Modern dining table under 800",
    "Velvet chair for bedroom",
    "Storage bed with budget of 1000",
  ];

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError("Please upload an image file (JPEG, PNG, WebP)");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("Image file too large (max 10MB)");
      return;
    }

    setSelectedImage(file);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Automatically search with image
    handleImageSearch(file);
  };

  const handleImageSearch = async (imageFile) => {
    if (!imageFile) return;

    setIsSearching(true);
    setError(null);
    setResults(null);

    try {
      const imageResults = await searchByImage(imageFile);
      console.log("Image Search Results:", imageResults);

      // Match products from response
      const matchedProducts = imageResults
        .map((p) => {
          const fullProduct = products.find(
            (prod) => String(prod.id) === String(p.product_id)
          );
          return fullProduct ? { ...p, fullProduct } : null;
        })
        .filter((p) => p !== null);

      // Format as results similar to text search
      setResults({
        query: "Image Search",
        perfect_matches: matchedProducts,
        alternatives: [],
        over_budget_options: [],
        explanation: `Found ${matchedProducts.length} visually similar products`,
      });

      if (onResultsFound) {
        onResultsFound(matchedProducts);
      }
    } catch (err) {
      setError("Image search failed. Please try again.");
      console.error("Image search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    setResults(null);
  };

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
      {/* Search Mode Tabs */}
      <div className={styles.searchModeTabs}>
        <button
          type="button"
          className={`${styles.modeTab} ${searchMode === "text" ? styles.activeTab : ""}`}
          onClick={() => {
            setSearchMode("text");
            clearImage();
          }}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          Text Search
        </button>
        <button
          type="button"
          className={`${styles.modeTab} ${searchMode === "image" ? styles.activeTab : ""}`}
          onClick={() => setSearchMode("image")}
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          Image Search
        </button>
      </div>

      {/* Text Search Form */}
      {searchMode === "text" && (
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
      )}

      {/* Image Search Form */}
      {searchMode === "image" && (
        <div className={styles.imageSearchForm}>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleImageUpload}
            className={styles.fileInput}
            id="imageUpload"
          />
          
          {!imagePreview ? (
            <label htmlFor="imageUpload" className={styles.uploadLabel}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <span className={styles.uploadText}>
                <strong>Click to upload an image</strong>
                <span className={styles.uploadHint}>or drag and drop</span>
                <span className={styles.uploadFormats}>PNG, JPG, WebP (max 10MB)</span>
              </span>
            </label>
          ) : (
            <div className={styles.imagePreviewContainer}>
              <img src={imagePreview} alt="Upload preview" className={styles.imagePreview} />
              <div className={styles.imageActions}>
                <button
                  type="button"
                  onClick={clearImage}
                  className={styles.clearImageButton}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                  Clear Image
                </button>
                <label htmlFor="imageUpload" className={styles.changeImageButton}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  Upload Different Image
                </label>
              </div>
              {isSearching && (
                <div className={styles.searchingOverlay}>
                  <span className={styles.spinner}></span>
                  Searching for similar products...
                </div>
              )}
            </div>
          )}
        </div>
      )}

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

      {/* Examples - Only show for text search */}
      {searchMode === "text" && !results && !error && (
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
                <span className={styles.analysisLabel}>Search:</span>
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
                        <div className={styles.analysisContent}>
                          <div className={styles.analysisHeader}>
                            <div className={styles.badgeRow}>
                              <span className={styles.analysisBadge}>Trade-off</span>
                              {item.compromise.summary.match(/\d+%/) && (
                                <span className={styles.savingsBadge}>
                                  {item.compromise.summary.match(/\d+%/)[0]} savings
                                </span>
                              )}
                            </div>
                            
                          </div>
                          
                          {item.compromise.advantages &&
                            item.compromise.advantages.length > 0 && (
                              <div className={styles.advantagesList}>
                                <span className={styles.advantagesTitle}>
                                  Advantages:
                                </span>
                                <ul>
                                  {item.compromise.advantages.map((adv, idx) => (
                                    <li key={idx}>{adv.replace(/\$(\d+)/g, '$1 TND')}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          {item.compromise.disadvantages &&
                            item.compromise.disadvantages.length > 0 && (
                              <div className={styles.disadvantagesList}>
                                <span className={styles.disadvantagesTitle}>
                                  Trade-offs:
                                </span>
                                <ul>
                                  {item.compromise.disadvantages.map(
                                    (dis, idx) => (
                                      <li key={idx}>{dis.replace(/\$(\d+)/g, '$1 TND')}</li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}
                        </div>
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
                          <div className={styles.analysisContent}>
                            <div className={styles.analysisHeader}>
                              <div className={styles.badgeRow}>
                                <span className={styles.analysisBadge}>Premium</span>
                                {item.compromise.summary.match(/\d+%/) && (
                                  <span className={styles.savingsBadge}>
                                    {item.compromise.summary.match(/\d+%/)[0]} over budget
                                  </span>
                                )}
                              </div>
                              <h4 className={styles.analysisTitle}>
                                {item.compromise.summary
                                  .replace(/^[^:]+:\s*/i, '')
                                  .replace(/\$(\d+)/g, '$1 TND')}
                              </h4>
                            </div>
                            
                            {item.compromise.advantages &&
                              item.compromise.advantages.length > 0 && (
                                <div className={styles.advantagesList}>
                                  <span className={styles.advantagesTitle}>
                                    Advantages:
                                  </span>
                                  <ul>
                                    {item.compromise.advantages.map(
                                      (adv, idx) => (
                                        <li key={idx}>{adv.replace(/\$(\d+)/g, '$1 TND')}</li>
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
                                        <li key={idx}>{dis.replace(/\$(\d+)/g, '$1 TND')}</li>
                                      ),
                                    )}
                                  </ul>
                                </div>
                              )}
                          </div>
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
