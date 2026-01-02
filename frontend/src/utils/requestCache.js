/**
 * Simple request cache to prevent duplicate simultaneous API calls
 * This helps prevent the "thundering herd" problem where multiple components
 * make the same API call at the same time.
 */

const requestCache = new Map();

/**
 * Cached fetch wrapper that deduplicates requests
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @param {number} cacheTime - How long to cache the request in milliseconds
 * @returns {Promise} - The fetch promise
 */
export const cachedFetch = async (url, options = {}, cacheTime = 2000) => {
  const cacheKey = `${url}-${JSON.stringify(options)}`;
  
  // Check if request is in flight or recently completed
  if (requestCache.has(cacheKey)) {
    const cached = requestCache.get(cacheKey);
    if (Date.now() - cached.timestamp < cacheTime) {
      console.log(`[RequestCache] Using cached request for: ${url}`);
      return cached.promise;
    }
  }
  
  console.log(`[RequestCache] Making new request for: ${url}`);
  
  // Make new request
  const promise = fetch(url, options);
  requestCache.set(cacheKey, {
    promise,
    timestamp: Date.now()
  });
  
  // Clean up after cache expires
  promise.finally(() => {
    setTimeout(() => {
      requestCache.delete(cacheKey);
    }, cacheTime);
  });
  
  return promise;
};

/**
 * Clear all cached requests
 */
export const clearRequestCache = () => {
  requestCache.clear();
};

/**
 * Clear a specific cached request
 * @param {string} url - The URL to clear from cache
 */
export const clearCachedRequest = (url) => {
  for (const [key] of requestCache) {
    if (key.startsWith(url)) {
      requestCache.delete(key);
    }
  }
};
