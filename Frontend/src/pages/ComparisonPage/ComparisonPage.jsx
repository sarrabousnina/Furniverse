import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import styles from './ComparisonPage.module.css';

const ComparisonPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const productAId = searchParams.get('productA');
  const productBId = searchParams.get('productB');

  // Text-to-speech functionality
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US'; // Force English (US)
      utterance.rate = 0.9; // Slightly slower for clarity
      utterance.pitch = 1;
      utterance.volume = 1;
      
      utterance.onstart = () => setIsPlaying(true);
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    }
  };

  // Fetch comparison data
  useEffect(() => {
    if (!productAId || !productBId) {
      setError('Please select two products to compare');
      setLoading(false);
      return;
    }

    const fetchComparison = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/compare/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_a_id: parseInt(productAId),
            product_b_id: parseInt(productBId)
          })
        });

        if (!response.ok) throw new Error('Failed to compare products');
        
        const data = await response.json();
        setComparison(data);
        
        // Animate steps sequentially
        animateSteps();
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [productAId, productBId]);

  const animateSteps = () => {
    let step = 0;
    const interval = setInterval(() => {
      step++;
      setCurrentStep(step);
      if (step >= 4) clearInterval(interval);
    }, 400);
  };

  // Generate voice narration
  const narrateComparison = () => {
    if (!comparison) return;

    const { product_a, product_b, visual_similarity, price_analysis, ai_recommendation } = comparison;
    
    const narration = `
      AI Product Comparison Results.
      
      Comparing ${product_a.name} at ${product_a.price} TND, 
      with ${product_b.name} at ${product_b.price} TND.
      
      Visual Analysis: These products have a ${visual_similarity.verdict.toLowerCase()} appearance, 
      with ${Math.round(visual_similarity.score * 100)}% similarity.
      
      ${price_analysis.verdict}.
      
      Perfect Use Cases:
      ${product_a.name} is ideal for ${ai_recommendation.reasons_for_a.join(', ')}.
      ${product_b.name} excels when ${ai_recommendation.reasons_for_b.join(', ')}.
      
      Both are excellent choices - select based on your specific needs.
    `.replace(/\s+/g, ' ').trim();

    speak(narration);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loadingContainer}>
          <div className={styles.aiThinking}>
            <div className={styles.aiIcon}>🤖</div>
            <h2>AI is analyzing products...</h2>
            <div className={styles.loadingSteps}>
              <div className={`${styles.step} ${currentStep >= 1 ? styles.active : ''}`}>
                📊 Loading product data
              </div>
              <div className={`${styles.step} ${currentStep >= 2 ? styles.active : ''}`}>
                🎨 Analyzing visual similarity with CLIP
              </div>
              <div className={`${styles.step} ${currentStep >= 3 ? styles.active : ''}`}>
                💎 Comparing features & styles
              </div>
              <div className={`${styles.step} ${currentStep >= 4 ? styles.active : ''}`}>
                ✨ Generating personalized insights
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>❌ {error}</h2>
          <button onClick={() => navigate('/shop')} className={styles.backButton}>
            Back to Shop
          </button>
        </div>
      </div>
    );
  }

  if (!comparison) return null;

  const { product_a, product_b, visual_similarity, price_analysis, feature_comparison, style_analysis, ai_recommendation } = comparison;

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <button onClick={() => navigate(-1)} className={styles.backBtn}>
          ← Back
        </button>
        <h1 className={styles.title}>
          <span className={styles.aiIcon}>🤖</span>
          AI Product Comparison
        </h1>
        <button 
          onClick={isPlaying ? stopSpeech : narrateComparison} 
          className={styles.voiceButton}
        >
          {isPlaying ? '🔇 Stop' : '🔊 Listen to Analysis'}
        </button>
      </div>

      {/* Products Side-by-Side */}
      <div className={styles.productsGrid}>
        <div className={styles.productCard}>
          <div className={styles.productBadge}>Option A</div>
          <img src={product_a.image} alt={product_a.name} className={styles.productImage} />
          <h3>{product_a.name}</h3>
          <p className={styles.price}>{product_a.price} TND</p>
        </div>

        <div className={styles.vsSection}>
          <div className={styles.vsCircle}>VS</div>
          <div className={styles.similarityBadge}>
            {Math.round(visual_similarity.score * 100)}% Similar
          </div>
        </div>

        <div className={styles.productCard}>
          <div className={styles.productBadge}>Option B</div>
          <img src={product_b.image} alt={product_b.name} className={styles.productImage} />
          <h3>{product_b.name}</h3>
          <p className={styles.price}>{product_b.price} TND</p>
        </div>
      </div>

      {/* Analysis Sections */}
      <div className={styles.analysisGrid}>
        
        {/* Visual Similarity */}
        <div className={`${styles.analysisCard} ${styles.fadeIn}`} style={{ animationDelay: '0.1s' }}>
          <h3>🎨 Visual Similarity</h3>
          <div className={styles.progressBar}>
            <div 
              className={styles.progressFill} 
              style={{ width: `${visual_similarity.score * 100}%` }}
            />
          </div>
          <p className={styles.verdict}>{visual_similarity.verdict}</p>
          <p className={styles.explanation}>{visual_similarity.explanation}</p>
        </div>

        {/* Price Analysis */}
        <div className={`${styles.analysisCard} ${styles.fadeIn}`} style={{ animationDelay: '0.2s' }}>
          <h3>💰 Price Analysis</h3>
          <div className={styles.priceComparison}>
            <div className={styles.priceItem}>
              <span className={styles.label}>Option A</span>
              <span className={styles.amount}>{product_a.price} TND</span>
            </div>
            <div className={styles.priceItem}>
              <span className={styles.label}>Option B</span>
              <span className={styles.amount}>{product_b.price} TND</span>
            </div>
          </div>
          <p className={styles.verdict}>{price_analysis.verdict}</p>
          {price_analysis.difference !== 0 && (
            <p className={styles.savingsNote}>
              💡 {price_analysis.difference > 0 ? 'Option B' : 'Option A'} costs 
              {Math.abs(price_analysis.difference)} TND {price_analysis.difference > 0 ? 'more' : 'less'}
            </p>
          )}
        </div>

        {/* Features */}
        <div className={`${styles.analysisCard} ${styles.fadeIn}`} style={{ animationDelay: '0.3s' }}>
          <h3>⚡ Features Comparison</h3>
          
          {feature_comparison.common_features.length > 0 && (
            <div className={styles.featureSection}>
              <h4>✓ Both Include</h4>
              <ul className={styles.featureList}>
                {feature_comparison.common_features.map((feature, idx) => (
                  <li key={idx} className={styles.commonFeature}>{feature}</li>
                ))}
              </ul>
            </div>
          )}

          <div className={styles.featuresRow}>
            <div className={styles.uniqueFeatures}>
              <h4>💎 Option A Exclusive</h4>
              <ul className={styles.featureList}>
                {feature_comparison.unique_to_a.length > 0 ? (
                  feature_comparison.unique_to_a.map((feature, idx) => (
                    <li key={idx} className={styles.uniqueFeature}>{feature}</li>
                  ))
                ) : (
                  <li className={styles.noFeatures}>Standard features</li>
                )}
              </ul>
            </div>

            <div className={styles.uniqueFeatures}>
              <h4>💎 Option B Exclusive</h4>
              <ul className={styles.featureList}>
                {feature_comparison.unique_to_b.length > 0 ? (
                  feature_comparison.unique_to_b.map((feature, idx) => (
                    <li key={idx} className={styles.uniqueFeature}>{feature}</li>
                  ))
                ) : (
                  <li className={styles.noFeatures}>Standard features</li>
                )}
              </ul>
            </div>
          </div>
        </div>

        {/* Style Compatibility */}
        <div className={`${styles.analysisCard} ${styles.fadeIn}`} style={{ animationDelay: '0.4s' }}>
          <h3>🎭 Style Analysis</h3>
          <p className={styles.compatibility}>{style_analysis.compatibility}</p>
          
          {style_analysis.common_styles.length > 0 && (
            <div className={styles.styleSection}>
              <h4>Shared Aesthetics</h4>
              <div className={styles.styleTags}>
                {style_analysis.common_styles.map((style, idx) => (
                  <span key={idx} className={styles.styleTag}>{style}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Recommendations */}
      <div className={`${styles.recommendationSection} ${styles.fadeIn}`} style={{ animationDelay: '0.5s' }}>
        <div className={styles.recommendationHeader}>
          <h2>🤖 AI Personalized Insights</h2>
          <div className={styles.confidence}>
            Confidence: {ai_recommendation.confidence}%
          </div>
        </div>

        <p className={styles.mainRecommendation}>{ai_recommendation.visual_similarity_note}</p>

        <div className={styles.useCasesGrid}>
          {/* Option A Use Cases */}
          <div className={styles.useCase}>
            <h3>✨ When to Choose {product_a.name}</h3>
            <ul className={styles.reasonsList}>
              {ai_recommendation.reasons_for_a.map((reason, idx) => (
                <li key={idx} className={styles.reason}>
                  <span className={styles.checkmark}>✓</span>
                  {reason}
                </li>
              ))}
            </ul>
          </div>

          {/* Option B Use Cases */}
          <div className={styles.useCase}>
            <h3>✨ When to Choose {product_b.name}</h3>
            <ul className={styles.reasonsList}>
              {ai_recommendation.reasons_for_b.map((reason, idx) => (
                <li key={idx} className={styles.reason}>
                  <span className={styles.checkmark}>✓</span>
                  {reason}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className={styles.finalNote}>
          <p>
            <strong>💡 Bottom Line:</strong> Both products are excellent choices! 
            Choose based on which features and use cases align best with your needs.
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className={styles.actions}>
        <button 
          onClick={() => window.open(`/products/${product_a.id}`, '_blank')}
          className={styles.viewButton}
        >
          View {product_a.name} Details
        </button>
        <button 
          onClick={() => window.open(`/products/${product_b.id}`, '_blank')}
          className={styles.viewButton}
        >
          View {product_b.name} Details
        </button>
      </div>
    </div>
  );
};

export default ComparisonPage;
