# Cost and Latency Notes

This document provides guidance on cost optimization, latency management, and performance tuning for the Restaurant Recommendation API deployed on Vercel (frontend) and Render (backend).

## Candidate Cap

### Current Configuration
- **Default**: 15 candidates sent to LLM for ranking
- **Setting**: `MAX_CANDIDATES_FOR_LLM` in `app/config.py`
- **Impact**: 
  - Higher cap = better recommendations but higher cost and latency
  - Lower cap = faster and cheaper but potentially less relevant recommendations

### Recommendations
- **Development**: Keep at 15 for testing
- **Production**: Start with 10-15, monitor costs
- **High Traffic**: Consider reducing to 8-10 if cost is a concern

### Cost Impact
- **OpenRouter free tier**: Limited tokens per day
- **Groq free tier**: Limited requests per day
- **Paid tiers**: Cost scales with token usage
- **Vercel**: Free tier includes 100GB bandwidth/month, $20/100GB overage
- **Render**: Free tier includes 750 hours/month, $7/month for paid tier with more hours

## Model Selection

### OpenRouter
- **Free Model**: `openrouter/free`
- **Pros**: No cost, good for development
- **Cons**: Rate limits, variable quality, slower response times
- **Paid Models**: Consider `openai/gpt-3.5-turbo` or `anthropic/claude-3-haiku` for production

### Groq
- **Free Model**: `llama-3.1-8b-instant`
- **Pros**: Very fast, good quality, generous free tier
- **Cons**: Rate limits on free tier
- **Paid Models**: `llama-3.1-70b` for higher quality (if needed)

### Recommendations
- **Development**: Use Groq free tier (faster)
- **Production**: Use Groq paid tier or OpenRouter paid models for reliability
- **Cost-Sensitive**: Stick with Groq free tier and implement caching

## When to Raise Load Limits

### Indicators
- **High Error Rate**: >5% of requests failing due to rate limits
- **Slow Response Times**: >5s average latency
- **User Complaints**: Reports of timeouts or slow loading

### Actions
1. **Increase Candidate Cap**: If recommendations are poor quality
2. **Upgrade API Plan**: If hitting rate limits
3. **Add Caching**: If same queries repeated frequently
4. **Optimize Prompt**: Reduce prompt length to save tokens

### Load Limits to Monitor
- **API Rate Limits**: Track requests per minute
- **Token Usage**: Monitor tokens per request
- **Response Time**: Track p50, p95, p99 latencies
- **Error Rate**: Track 429 (rate limit) and 500 errors

## Caching Strategies

### In-Memory Caching (Recommended for Development)
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_recommendations(location, budget, cuisine, min_rating, top_n):
    # Call recommendation logic
    pass
```

**Pros**: Simple, fast, no external dependencies
**Cons**: Lost on restart, limited to single process

### Redis Caching (Recommended for Production)
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_recommendations(cache_key):
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    # Compute and cache
    result = compute_recommendations(...)
    r.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
    return result
```

**Pros**: Persistent, shared across processes, configurable TTL
**Cons**: Requires Redis infrastructure

### Vercel Edge Config (Recommended for Vercel Deployment)
Vercel Edge Config provides a globally distributed key-value store with low latency.
- **Pros**: Built into Vercel, global CDN, no additional infrastructure
- **Cons**: Limited to 256KB per value, not suitable for large datasets
- **Use Case**: Cache API responses, not full dataset

### Render Redis (Recommended for Render Deployment)
Render offers managed Redis as an add-on.
- **Pros**: Managed service, integrates with Render apps
- **Cons**: Additional cost (~$15/month for basic tier)
- **Use Case**: Production caching for Render backend

### Cache Key Strategy
Include all relevant parameters:
```python
cache_key = f"rec:{location}:{budget}:{cuisine}:{min_rating}:{top_n}"
```

### Cache TTL Recommendations
- **Popular Queries**: 1-4 hours
- **Less Popular**: 30 minutes
- **Real-time Requirements**: 5-10 minutes or no caching

## Latency Optimization

### Current Latency Breakdown
1. **Dataset Loading**: ~500ms (first request)
2. **Filtering**: ~50-100ms
3. **LLM Call**: ~1-3s (Groq), ~2-5s (OpenRouter free)
4. **Response Processing**: ~50ms
5. **Vercel Cold Start**: ~500ms-2s (first request after inactivity)
6. **Render Cold Start**: ~1-3s (first request after inactivity)

**Total**: ~2-11s depending on LLM provider and cold starts

### Optimization Strategies

#### 1. Pre-load Dataset
```python
# Load at startup instead of per request
df = load_restaurants_df()
```
**Impact**: Saves ~500ms per request
**Trade-off**: Higher memory usage

#### 2. Use Faster LLM
- Groq is generally faster than OpenRouter free tier
- Consider paid models for consistent low latency

#### 3. Parallel Processing
```python
# Filter and prompt building in parallel
```
**Impact**: Minor savings (~50-100ms)

#### 4. Reduce Candidate Cap
- Lower cap = faster LLM processing
- Impact: ~100-200ms per 5 candidates reduced

### Latency Targets
- **p50**: <3s (adjusted for serverless cold starts)
- **p95**: <5s
- **p99**: <8s

### Serverless-Specific Optimizations
- **Keep Render Instance Warm**: Use a cron job or external monitoring to ping the endpoint every 5-10 minutes
- **Vercel ISR**: Use Incremental Static Regeneration for static content
- **Edge Functions**: Consider using Vercel Edge Functions for faster response times in some regions

## Cost Monitoring

### Metrics to Track
- **Total Requests**: Per day/hour
- **Tokens Used**: Per request and total
- **API Costs**: By provider
- **Cache Hit Rate**: Percentage of requests served from cache

### Cost Estimation
- **Groq Free Tier**: ~100 requests/day (varies)
- **OpenRouter Free Tier**: ~50 requests/day (varies)
- **Paid Groq**: ~$0.59 per million tokens
- **Paid OpenRouter**: Varies by model
- **Vercel Free Tier**: 100GB bandwidth/month, unlimited deployments
- **Render Free Tier**: 750 hours/month, 512MB RAM
- **Render Paid Tier**: $7/month for more hours and resources

### Budget Alerts
Set up alerts when:
- Daily cost exceeds $X
- Token usage exceeds Y% of quota
- Error rate exceeds Z%

## Production Checklist

Before deploying to production:
- [ ] Implement caching strategy
- [ ] Set up monitoring and alerts
- [ ] Configure paid API keys if needed
- [ ] Tune candidate cap based on testing
- [ ] Set appropriate cache TTLs
- [ ] Document cost limits and escalation procedures
- [ ] Test under load
- [ ] Have rollback plan ready
- [ ] Configure FRONTEND_URL environment variable on Render
- [ ] Configure NEXT_PUBLIC_API_URL environment variable on Vercel
- [ ] Set up CORS to allow Vercel domain
- [ ] Test cold start behavior on both platforms
