import numpy as np
from typing import Dict, List, Optional
import time

class AggregatorAgent:
    """Agent responsible for aggregating fundamental and sentiment analysis"""
    
    def __init__(self):
        self.recommendation_thresholds = {
            'buy': 70,      # Score >= 70 = BUY
            'hold_upper': 40, # Score 40-69 = HOLD
            'sell': 40      # Score < 40 = SELL
        }
    
    def aggregate_scores(
        self, 
        ticker: str,
        company_name: str,
        screening_data: Dict,
        fundamental_data: Dict,
        sentiment_data: Dict,
        fundamental_weight: float = 0.5,
        sentiment_weight: float = 0.5
    ) -> Dict:
        """
        Aggregate fundamental and sentiment scores with weighted combination
        
        Args:
            ticker: Stock ticker
            company_name: Company name
            screening_data: Data from screening agent
            fundamental_data: Data from fundamental agent
            sentiment_data: Data from sentiment agent
            fundamental_weight: Weight for fundamental analysis (0-1)
            sentiment_weight: Weight for sentiment analysis (0-1)
            
        Returns:
            Dictionary with aggregated analysis and recommendation
        """
        try:
            # Normalize weights to ensure they sum to 1
            total_weight = fundamental_weight + sentiment_weight
            if total_weight > 0:
                fundamental_weight = fundamental_weight / total_weight
                sentiment_weight = sentiment_weight / total_weight
            else:
                fundamental_weight = sentiment_weight = 0.5
            
            # Calculate individual scores
            fundamental_score = self._calculate_fundamental_score(fundamental_data)
            sentiment_score = self._calculate_sentiment_score(sentiment_data)
            
            # Calculate weighted overall score
            overall_score = (
                fundamental_score * fundamental_weight + 
                sentiment_score * sentiment_weight
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(overall_score)
            
            # Create reasoning
            reasoning = self._generate_reasoning(
                fundamental_score, 
                sentiment_score, 
                overall_score, 
                fundamental_data, 
                sentiment_data
            )
            
            # Compile result
            result = {
                'ticker': ticker,
                'company_name': company_name,
                'overall_score': round(overall_score, 1),
                'fundamental_score': round(fundamental_score, 1),
                'sentiment_score': round(sentiment_score, 1),
                'recommendation': recommendation,
                'reasoning': reasoning,
                'weights_used': {
                    'fundamental': round(fundamental_weight * 100, 1),
                    'sentiment': round(sentiment_weight * 100, 1)
                },
                'analysis_timestamp': time.time(),
                
                # Include key metrics for display
                'current_price': fundamental_data.get('current_price', 'N/A'),
                'market_cap': fundamental_data.get('market_cap', 'N/A'),
                'pe_ratio': fundamental_data.get('pe_ratio', 'N/A'),
                'pb_ratio': fundamental_data.get('pb_ratio', 'N/A'),
                'roe': fundamental_data.get('roe', 'N/A'),
                'avg_sentiment': sentiment_data.get('avg_sentiment', 'N/A'),
                'positive_count': sentiment_data.get('positive_count', 0),
                'negative_count': sentiment_data.get('negative_count', 0),
                'total_articles': sentiment_data.get('total_articles', 0),
                
                # Data quality indicators
                'fundamental_quality': fundamental_data.get('data_quality', 'unknown'),
                'sentiment_quality': 'good' if sentiment_data.get('total_articles', 0) > 0 else 'poor'
            }
            
            return result
            
        except Exception as e:
            print(f"Error aggregating scores for {ticker}: {e}")
            return self._get_error_result(ticker, company_name, str(e))
    
    def _calculate_fundamental_score(self, fundamental_data: Dict) -> float:
        """Calculate fundamental analysis score (0-100)"""
        try:
            score = 50.0  # Start with neutral score
            
            # PE Ratio scoring (25 points max)
            pe_ratio = fundamental_data.get('pe_ratio')
            if pe_ratio is not None and pe_ratio > 0:
                if pe_ratio < 15:
                    score += 25  # Excellent valuation
                elif pe_ratio < 20:
                    score += 20  # Good valuation
                elif pe_ratio < 25:
                    score += 15  # Fair valuation
                elif pe_ratio < 35:
                    score += 5   # High but acceptable
                else:
                    score -= 10  # Overvalued
            
            # PB Ratio scoring (15 points max)
            pb_ratio = fundamental_data.get('pb_ratio')
            if pb_ratio is not None and pb_ratio > 0:
                if pb_ratio < 1.5:
                    score += 15  # Excellent book value
                elif pb_ratio < 3:
                    score += 10  # Good book value
                elif pb_ratio < 5:
                    score += 5   # Fair book value
                else:
                    score -= 5   # High book value
            
            # ROE scoring (20 points max)
            roe = fundamental_data.get('roe')
            if roe is not None:
                roe_percent = roe * 100 if roe < 1 else roe  # Handle decimal vs percentage
                if roe_percent > 20:
                    score += 20  # Excellent returns
                elif roe_percent > 15:
                    score += 15  # Good returns
                elif roe_percent > 10:
                    score += 10  # Fair returns
                elif roe_percent > 5:
                    score += 5   # Low returns
                else:
                    score -= 5   # Poor returns
            
            # Profit Margin scoring (10 points max)
            profit_margin = fundamental_data.get('profit_margin')
            if profit_margin is not None:
                margin_percent = profit_margin * 100 if profit_margin < 1 else profit_margin
                if margin_percent > 20:
                    score += 10
                elif margin_percent > 10:
                    score += 7
                elif margin_percent > 5:
                    score += 4
                elif margin_percent > 0:
                    score += 2
                else:
                    score -= 5
            
            # Debt to Equity scoring (10 points max)
            debt_to_equity = fundamental_data.get('debt_to_equity')
            if debt_to_equity is not None:
                if debt_to_equity < 0.3:
                    score += 10  # Low debt
                elif debt_to_equity < 0.6:
                    score += 7   # Moderate debt
                elif debt_to_equity < 1.0:
                    score += 3   # Higher debt
                else:
                    score -= 5   # High debt
            
            # Revenue growth (bonus points)
            revenue_growth = fundamental_data.get('revenue_growth')
            if revenue_growth is not None:
                growth_percent = revenue_growth * 100 if revenue_growth < 1 else revenue_growth
                if growth_percent > 20:
                    score += 5
                elif growth_percent > 10:
                    score += 3
                elif growth_percent < -10:
                    score -= 5
            
            # Ensure score is within bounds
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error calculating fundamental score: {e}")
            return 50.0  # Return neutral score on error
    
    def _calculate_sentiment_score(self, sentiment_data: Dict) -> float:
        """Calculate sentiment analysis score (0-100)"""
        try:
            # Base score
            score = 50.0
            
            # Average sentiment scoring (40 points max)
            avg_sentiment = sentiment_data.get('avg_sentiment', 0.0)
            if avg_sentiment is not None:
                # Convert VADER score (-1 to 1) to 0-40 point scale
                sentiment_points = (avg_sentiment + 1) * 20  # Scale to 0-40
                score += sentiment_points - 20  # Adjust so 0 sentiment = no change
            
            # Article count scoring (20 points max)
            total_articles = sentiment_data.get('total_articles', 0)
            if total_articles >= 10:
                score += 20  # Good coverage
            elif total_articles >= 5:
                score += 15  # Fair coverage
            elif total_articles >= 2:
                score += 10  # Limited coverage
            elif total_articles >= 1:
                score += 5   # Minimal coverage
            # No articles = no points
            
            # Positive vs negative ratio (20 points max)
            positive_count = sentiment_data.get('positive_count', 0)
            negative_count = sentiment_data.get('negative_count', 0)
            total_sentiment_articles = positive_count + negative_count
            
            if total_sentiment_articles > 0:
                positive_ratio = positive_count / total_sentiment_articles
                if positive_ratio >= 0.8:
                    score += 20  # Overwhelmingly positive
                elif positive_ratio >= 0.6:
                    score += 15  # Mostly positive
                elif positive_ratio >= 0.4:
                    score += 5   # Balanced
                elif positive_ratio >= 0.2:
                    score -= 5   # Mostly negative
                else:
                    score -= 15  # Overwhelmingly negative
            
            # Sentiment volatility penalty (up to -10 points)
            sentiment_volatility = sentiment_data.get('sentiment_volatility', 0.0)
            if sentiment_volatility > 0.5:
                score -= 10  # High volatility is bad
            elif sentiment_volatility > 0.3:
                score -= 5   # Moderate volatility
            
            # Ensure score is within bounds
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error calculating sentiment score: {e}")
            return 50.0  # Return neutral score on error
    
    def _generate_recommendation(self, overall_score: float) -> str:
        """Generate BUY/HOLD/SELL recommendation based on overall score"""
        if overall_score >= self.recommendation_thresholds['buy']:
            return 'BUY'
        elif overall_score >= self.recommendation_thresholds['hold_upper']:
            return 'HOLD'
        else:
            return 'SELL'
    
    def _generate_reasoning(
        self, 
        fundamental_score: float, 
        sentiment_score: float, 
        overall_score: float,
        fundamental_data: Dict,
        sentiment_data: Dict
    ) -> str:
        """Generate human-readable reasoning for the recommendation"""
        try:
            ticker = fundamental_data.get('ticker', 'the stock')
            company_name = fundamental_data.get('company_name', ticker)
            
            # 1. Overall assessment
            if overall_score >= 75:
                verdict = f"{company_name} ({ticker}) exhibits a highly attractive risk-reward profile with an overall rating of {overall_score:.1f}/100."
            elif overall_score >= 55:
                verdict = f"Our model rates {company_name} ({ticker}) as moderately favorable at {overall_score:.1f}/100, showing steady performance indicators."
            elif overall_score >= 40:
                verdict = f"Analysis yields a neutral outlook for {company_name} ({ticker}) at {overall_score:.1f}/100, due to conflicting fundamental and sentiment trends."
            else:
                verdict = f"Caution is advised for {company_name} ({ticker}) with an overall score of {overall_score:.1f}/100, indicating elevated risks."

            # 2. Fundamentals details
            fund_desc = []
            pe_val = fundamental_data.get('pe_ratio')
            roe_val = fundamental_data.get('roe')
            debt_to_equity = fundamental_data.get('debt_to_equity')
            
            if pe_val is not None:
                if pe_val < 15:
                    fund_desc.append(f"is trading at a attractive valuation (P/E ratio of {pe_val:.1f})")
                elif pe_val > 35:
                    fund_desc.append(f"is trading at a premium valuation (P/E ratio of {pe_val:.1f})")
                else:
                    fund_desc.append(f"displays a fair P/E valuation of {pe_val:.1f}")
            
            if roe_val is not None:
                roe_percent = roe_val * 100 if roe_val < 1 else roe_val
                if roe_percent > 18:
                    fund_desc.append(f"shows high capital efficiency with an ROE of {roe_percent:.1f}%")
                elif roe_percent < 8:
                    fund_desc.append(f"reports soft profitability with an ROE of {roe_percent:.1f}%")
            
            if debt_to_equity is not None:
                if debt_to_equity > 1.2:
                    fund_desc.append(f"faces leverage pressure with a debt-to-equity ratio of {debt_to_equity:.2f}")
                elif debt_to_equity < 0.3:
                    fund_desc.append(f"maintains a clean balance sheet with low leverage (D/E of {debt_to_equity:.2f})")
            
            if fund_desc:
                fund_sentence = f"Fundamentally, the company {', '.join(fund_desc)}."
            else:
                fund_sentence = f"Fundamental analysis score stands at {fundamental_score:.1f}/100."

            # 3. Sentiment details
            avg_sent = sentiment_data.get('avg_sentiment', 0.0)
            total_articles = sentiment_data.get('total_articles', 0)
            pos_pct = sentiment_data.get('sentiment_distribution', {}).get('positive', 0)
            neg_pct = sentiment_data.get('sentiment_distribution', {}).get('negative', 0)
            
            if total_articles > 0:
                if avg_sent >= 0.15:
                    sent_sentence = f"Market sentiment is distinctly bullish (compound score of {avg_sent:.2f}), supported by {pos_pct}% positive articles across {total_articles} source(s)."
                elif avg_sent <= -0.15:
                    sent_sentence = f"Market sentiment is bearish (compound score of {avg_sent:.2f}), weighed down by {neg_pct}% negative reports across {total_articles} source(s)."
                else:
                    sent_sentence = f"News coverage is neutral (compound score of {avg_sent:.2f}) across {total_articles} article(s)."
            else:
                sent_sentence = "Limited news flow was detected, leaving sentiment baseline neutral."
                
            return f"{verdict} {fund_sentence} {sent_sentence}"
            
        except Exception as e:
            return f"Analysis completed with overall score of {overall_score:.1f}/100. Fundamentals scored {fundamental_score:.1f} and market sentiment scored {sentiment_score:.1f}."
    
    def _get_error_result(self, ticker: str, company_name: str, error_msg: str) -> Dict:
        """Return error result when aggregation fails"""
        return {
            'ticker': ticker,
            'company_name': company_name,
            'overall_score': 0.0,
            'fundamental_score': 0.0,
            'sentiment_score': 0.0,
            'recommendation': 'HOLD',
            'reasoning': f"Analysis failed: {error_msg}",
            'error': error_msg,
            'analysis_timestamp': time.time()
        }
    
    def batch_aggregate(self, stocks_data: List[Dict], weights: Dict) -> List[Dict]:
        """Aggregate multiple stocks at once"""
        results = []
        
        for stock_data in stocks_data:
            try:
                result = self.aggregate_scores(
                    ticker=stock_data.get('ticker', ''),
                    company_name=stock_data.get('company_name', ''),
                    screening_data=stock_data.get('screening_data', {}),
                    fundamental_data=stock_data.get('fundamental_data', {}),
                    sentiment_data=stock_data.get('sentiment_data', {}),
                    fundamental_weight=weights.get('fundamental', 0.5),
                    sentiment_weight=weights.get('sentiment', 0.5)
                )
                results.append(result)
            except Exception as e:
                print(f"Error processing {stock_data.get('ticker', 'unknown')}: {e}")
                continue
        
        return results
    
    def get_portfolio_summary(self, results: List[Dict]) -> Dict:
        """Generate portfolio-level summary statistics"""
        try:
            if not results:
                return {'error': 'No results to summarize'}
            
            scores = [r['overall_score'] for r in results if 'overall_score' in r]
            recommendations = [r['recommendation'] for r in results if 'recommendation' in r]
            
            return {
                'total_stocks': len(results),
                'average_score': round(np.mean(scores), 1) if scores else 0,
                'score_std': round(np.std(scores), 1) if scores else 0,
                'recommendation_distribution': {
                    'BUY': recommendations.count('BUY'),
                    'HOLD': recommendations.count('HOLD'),
                    'SELL': recommendations.count('SELL')
                },
                'top_performer': max(results, key=lambda x: x.get('overall_score', 0)) if results else None,
                'worst_performer': min(results, key=lambda x: x.get('overall_score', 100)) if results else None
            }
            
        except Exception as e:
            return {'error': f'Summary calculation failed: {str(e)}'}
