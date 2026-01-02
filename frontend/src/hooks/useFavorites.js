import { useState, useEffect, useCallback } from 'react';
import { API_URL } from '../config';
import { cachedFetch } from '../utils/requestCache';

export const useFavorites = (user) => {
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // Memoize the function so it doesn't change on every render
  // This prevents infinite loops in useEffect
  const fetchFavoritesCount = useCallback(async () => {
    if (!user) {
      setFavoritesCount(0);
      return;
    }

    setLoading(true);
    try {
      // Use cachedFetch to prevent duplicate simultaneous requests
      const response = await cachedFetch(`${API_URL}/users/me/favorites`, {
        credentials: 'include',
      }, 2000); // Cache for 2 seconds
      
      if (response.ok) {
        const data = await response.json();
        setFavoritesCount(data.count || 0);
      } else {
        setFavoritesCount(0);
      }
    } catch (error) {
      console.error('Error fetching favorites count:', error);
      setFavoritesCount(0);
    } finally {
      setLoading(false);
    }
  }, [user]); // Only recreate when user changes

  useEffect(() => {
    fetchFavoritesCount();
  }, [fetchFavoritesCount]); // Now safe to include in dependencies

  return {
    favoritesCount,
    loading,
    refetch: fetchFavoritesCount
  };
};