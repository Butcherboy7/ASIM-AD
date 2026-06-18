import requests
import os
from typing import Dict, List, Optional
import time
from datetime import datetime, timedelta
import re
import yfinance as yf
import xml.etree.ElementTree as ET

# NLP libraries
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

nlp = None


class SentimentAgent:
    """
    Sentiment analysis agent.

    Sources (no API key required):
      1. yfinance  – news attached to each ticker
      2. Google Finance RSS  – per-ticker RSS feed
      3. Yahoo Finance RSS   – per-ticker RSS feed

    Scoring: NLTK VADER compound score.
    """

    def __init__(self):
        self.cache: Dict = {}
        self.cache_duration = 3600  # 1 hour

        self.sia = None
        if NLTK_AVAILABLE:
            try:
                # Download required lexicon lazily on first instantiation (cached by Streamlit)
                nltk.download('vader_lexicon', quiet=True)
                self.sia = SentimentIntensityAnalyzer()
            except Exception:
                self.sia = None

        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_sentiment(self, ticker: str, company_name: str) -> Dict:
        cache_key = f"sentiment_{ticker}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']

        articles = self._fetch_all_articles(ticker, company_name)

        if not articles:
            result = self._neutral_sentiment(ticker, company_name, "No articles found")
        else:
            result = self._analyze_articles(articles)
            result.update({
                'ticker': ticker,
                'company_name': company_name,
                'analysis_timestamp': time.time(),
                'total_articles': len(articles),
                'data_source': 'yfinance + RSS feeds',
            })
            if nlp:
                result.update(self._ner_analysis(articles))

        self._cache(cache_key, result)
        return result

    def get_sentiment_summary(self, ticker: str) -> str:
        data = self.analyze_sentiment(ticker, ticker)
        score = data.get('avg_sentiment', 0.0)
        if score >= 0.1:
            return "Positive market sentiment"
        elif score <= -0.1:
            return "Negative market sentiment"
        return "Neutral market sentiment"

    # ------------------------------------------------------------------
    # Article fetching
    # ------------------------------------------------------------------

    def _fetch_all_articles(self, ticker: str, company_name: str) -> List[Dict]:
        import concurrent.futures
        articles = []
        
        # Fetch news sources concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._fetch_yfinance, ticker): "yfinance",
                executor.submit(self._fetch_google_rss, ticker, company_name): "google_rss",
                executor.submit(self._fetch_yahoo_rss, ticker): "yahoo_rss"
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    if res:
                        articles.extend(res)
                except Exception as e:
                    source_name = futures[future]
                    print(f"[SentimentAgent] Error fetching from {source_name}: {e}")

        # Deduplicate by title
        seen = set()
        unique = []
        for a in articles:
            key = a.get('title', '')[:80].lower()
            if key and key not in seen:
                seen.add(key)
                unique.append(a)

        return unique[:30]

    # ---- yfinance ----
    def _fetch_yfinance(self, ticker: str) -> List[Dict]:
        try:
            yf_ticker = self._resolve_yf_ticker(ticker)
            stock = yf.Ticker(yf_ticker)
            raw_news = stock.news or []
            articles = []
            for item in raw_news:
                pub_raw = item.get('providerPublishTime', time.time())
                try:
                    pub_time = datetime.fromtimestamp(pub_raw).strftime('%Y-%m-%dT%H:%M:%SZ')
                except Exception:
                    pub_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('summary', '') or item.get('description', ''),
                    'url': item.get('link', ''),
                    'publishedAt': pub_time,
                    'source': item.get('publisher', 'Yahoo Finance'),
                })
            return articles[:20]
        except Exception as e:
            print(f"[SentimentAgent] yfinance error for {ticker}: {e}")
            return []

    def _resolve_yf_ticker(self, ticker: str) -> str:
        if '.' in ticker:
            return ticker
        try:
            info = yf.Ticker(ticker).info
            if info and info.get('regularMarketPrice') and info.get('longName'):
                return ticker
        except Exception:
            pass
        return f"{ticker}.NS"

    # ---- Google Finance RSS ----
    def _fetch_google_rss(self, ticker: str, company_name: str) -> List[Dict]:
        # Perform 1 query instead of 2 to minimize network overhead and double latency
        q = company_name.split()[0] if company_name else ticker
        try:
            url = (
                f"https://news.google.com/rss/search"
                f"?q={requests.utils.quote(q + ' stock')}&hl=en-IN&gl=IN&ceid=IN:en"
            )
            resp = requests.get(url, headers=self.headers, timeout=3.5)
            if resp.status_code == 200:
                return self._parse_rss(resp.text, 'Google News')[:15]
        except Exception as e:
            print(f"[SentimentAgent] Google RSS error: {e}")
        return []

    # ---- Yahoo Finance RSS ----
    def _fetch_yahoo_rss(self, ticker: str) -> List[Dict]:
        yf_ticker = self._resolve_yf_ticker(ticker)
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={yf_ticker}&region=US&lang=en-US"
        try:
            resp = requests.get(url, headers=self.headers, timeout=3.5)
            if resp.status_code == 200:
                return self._parse_rss(resp.text, 'Yahoo Finance RSS')
        except Exception as e:
            print(f"[SentimentAgent] Yahoo RSS error: {e}")
        return []

    def _parse_rss(self, xml_text: str, source: str) -> List[Dict]:
        articles: List[Dict] = []
        try:
            root = ET.fromstring(xml_text)
            ns = {'dc': 'http://purl.org/dc/elements/1.1/'}
            for item in root.iter('item'):
                title = item.findtext('title', '').strip()
                desc = item.findtext('description', '').strip()
                # Strip HTML from description
                desc = re.sub(r'<[^>]+>', '', desc)
                pub = item.findtext('pubDate', '')
                link = item.findtext('link', '')
                articles.append({
                    'title': title,
                    'description': desc,
                    'url': link,
                    'publishedAt': pub,
                    'source': source,
                })
        except Exception as e:
            print(f"[SentimentAgent] RSS parse error: {e}")
        return articles

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def _analyze_articles(self, articles: List[Dict]) -> Dict:
        if not self.sia:
            return {
                'avg_sentiment': 0.0,
                'sentiment_distribution': {'positive': 0, 'neutral': 100, 'negative': 0},
                'error': 'NLTK VADER not available',
            }

        compound_scores: List[float] = []
        pos = neg = neu = 0
        detailed: List[Dict] = []

        for article in articles:
            text = ' '.join(filter(None, [
                article.get('title', ''),
                article.get('description', ''),
            ])).strip()
            if len(text) < 10:
                continue

            scores = self.sia.polarity_scores(text)
            c = scores['compound']
            compound_scores.append(c)

            if c >= 0.05:
                pos += 1
                label = 'positive'
            elif c <= -0.05:
                neg += 1
                label = 'negative'
            else:
                neu += 1
                label = 'neutral'

            detailed.append({
                'title': article.get('title', '')[:120],
                'sentiment_score': round(c, 3),
                'sentiment_label': label,
                'published_at': article.get('publishedAt', ''),
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
            })

        total = len(compound_scores)
        if total == 0:
            return self._neutral_sentiment('', '', 'No scoreable text')

        avg = sum(compound_scores) / total
        volatility = self._std(compound_scores)

        return {
            'avg_sentiment': round(avg, 3),
            'sentiment_range': [round(min(compound_scores), 3), round(max(compound_scores), 3)],
            'sentiment_volatility': round(volatility, 3),
            'positive_count': pos,
            'negative_count': neg,
            'neutral_count': neu,
            'sentiment_distribution': {
                'positive': round(pos / total * 100, 1),
                'negative': round(neg / total * 100, 1),
                'neutral': round(neu / total * 100, 1),
            },
            'detailed_analysis': detailed[:10],
            'analysis_method': 'NLTK VADER + yfinance/RSS',
        }

    def _ner_analysis(self, articles: List[Dict]) -> Dict:
        if not nlp:
            return {}
        try:
            entity_counts: Dict = {}
            for article in articles[:10]:
                text = ' '.join(filter(None, [
                    article.get('title', ''),
                    article.get('description', ''),
                ])).strip()
                if len(text) < 10:
                    continue
                doc = nlp(text)
                for ent in doc.ents:
                    if ent.label_ in ('PERSON', 'ORG', 'PRODUCT', 'EVENT'):
                        key = (ent.text, ent.label_)
                        entity_counts[key] = entity_counts.get(key, 0) + 1

            top = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            return {
                'top_entities': [
                    {'entity': e[0], 'label': e[1], 'mentions': c}
                    for (e, _), c in top
                ],
                'ner_model': 'spaCy en_core_web_sm',
            }
        except Exception as e:
            return {'ner_error': str(e)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _std(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _neutral_sentiment(self, ticker: str, company_name: str, reason: str) -> Dict:
        return {
            'ticker': ticker,
            'company_name': company_name,
            'avg_sentiment': 0.0,
            'sentiment_range': [0.0, 0.0],
            'sentiment_volatility': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 100},
            'total_articles': 0,
            'analysis_timestamp': time.time(),
            'note': reason,
            'analysis_method': 'fallback',
            'data_source': 'none',
        }

    def _is_cached(self, key: str) -> bool:
        if key not in self.cache:
            return False
        return (time.time() - self.cache[key]['timestamp']) < self.cache_duration

    def _cache(self, key: str, data: Dict):
        self.cache[key] = {'data': data, 'timestamp': time.time()}
