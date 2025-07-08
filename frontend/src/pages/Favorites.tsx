import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Trash2, Heart, ArrowLeft } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

type Favorite = {
  title: string;
  link: string;
  addedAt: string;
  image?: string;
  price?: string;
  rating?: number;
};
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const Favorites = () => {
  const [favorites, setFavorites] = useState<Favorite[]>([]);

  const fetchFavorites = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/favorites`);
      const data = await res.json();
      setFavorites(data.favorites || []);
    } catch (error) {
      toast.error('Fetching favorites');
    }
  };

  const removeFavorite = async (link: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/user/favorites`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ link }),
      });
      if (res.ok) {
        toast.success('Removed from favorites');
        fetchFavorites();
      } else {
        toast.error('Failed to remove favorite');
      }
    } catch (error) {
      toast.error('Error removing favorite');
    }
  };

  const handleProductAction = async (fav: Favorite) => {
    try {
      // You can route actions to specific agents based on the user's query or choice
      const response = await fetch(`${BACKEND_URL}/api/agent/product-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productLink: fav.link }),
      });

      const data = await response.json();
      if (response.ok) {
        toast.success(data.message || 'Action performed successfully');
      } else {
        toast.error('Error performing action');
      }
    } catch (error) {
      toast.error('Error performing action');
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-green-800">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        {/* Geri dönüş linki */}
        <Link
          to="/marketplace"
          className="flex items-center space-x-2 text-white hover:text-teal-300 transition-colors text-base font-medium"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to MarketPlace</span>
        </Link>
      </header>

      {/* Başlıq və yaşıl ürək */}
      <div className="flex justify-center items-center gap-4 mb-12 mt-6">
        <h1 className="text-5xl font-bold text-white text-center drop-shadow-[0_0_3px_#00ff99]">
          Favorites
        </h1>
        <motion.div
          animate={{ y: [0, -5, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        >
          <Heart className="w-10 h-10 text-green-400 drop-shadow-[0_0_4px_#00ff99]" />
        </motion.div>
      </div>

      {/* Favoritlər */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto px-4 pb-12">
        {favorites.length === 0 && (
          <p className="text-white col-span-full text-center">No favorites yet.</p>
        )}

        {favorites.map((fav, index) => (
          <Card key={index} className="bg-white/10 backdrop-blur-lg border-white/20 text-white">
            {fav.image && (
              <img
                src={fav.image}
                alt={fav.title}
                className="w-full h-48 object-cover rounded-t"
              />
            )}
            <CardHeader>
              <CardTitle className="text-xl">{fav.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {fav.rating && (
                <p className="text-yellow-400">⭐ {fav.rating.toFixed(1)}</p>
              )}
              {fav.price && (
                <p className="text-green-300">Price: {fav.price}</p>
              )}
              <a
                href={fav.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-teal-400 underline block"
              >
                View Product
              </a>
              <div className="flex space-x-4 mt-4">
                <button
                  onClick={() => handleProductAction(fav)}
                  className="flex items-center text-sm bg-teal-600 hover:bg-teal-700 px-3 py-1 rounded-md transition"
                >
                  <Heart className="w-4 h-4 mr-2" />
                  Take Action
                </button>
                <button
                  onClick={() => removeFavorite(fav.link)}
                  className="flex items-center text-sm bg-red-600 hover:bg-red-700 px-3 py-1 rounded-md transition"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Remove
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Favorites;
