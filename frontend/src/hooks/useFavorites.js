import { useState, useEffect } from 'react';
import { API_URL } from '../config';

export const useFavorites = (user) => {
  const [favoritesCount, setFavoritesCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchFavoritesCount = async () => {
    if (!user) {
      setFavoritesCount(0);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/users/me/favorites`, {
        credentials: 'include',
      });
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
  };

  useEffect(() => {
    fetchFavoritesCount();
  }, [user]);

  return {
    favoritesCount,
    loading,
    refetch: fetchFavoritesCount
  };
};