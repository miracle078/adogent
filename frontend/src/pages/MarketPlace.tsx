import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { ArrowLeft, Heart, PackageSearch } from 'lucide-react'; 
import { ShoppingCart } from 'lucide-react';
import { motion } from "framer-motion";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const MarketPlace = () => {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);

  const categories = [
    { name: "Luxury Cars", value: "cars" },
    { name: "Watches", value: "watches" },
    { name: "Designer Clothing", value: "clothing" },
    { name: "Real Estate", value: "real_estate" },
  ];

  // Dummy Data for Products
  const dummyProducts = [
    {
      id: 1,
      name: "Rolls Royce Phantom",
      price: 450000,
      image: "/images/rolls-royce.jpg",
      url: "https://www.rolls-roycemotorcars.com",
    },
    {
      id: 2,
      name: "Rolex Submariner",
      price: 8000,
      image: "/images/rolex-submariner.webp",
      url: "https://www.rolex.com",
    },
    {
      id: 3,
      name: "Chanel Classic Flap Bag",
      price: 5000,
      image: "/images/bag.webp",
      url: "https://www.chanel.com",
    },
    {
      id: 4,
      name: "Luxury Apartment in London",
      price: 12000000,
      image: "/images/apartment.jpg",
      url: "https://www.luxuryproperty.com",
    },
  ];

  // Function to fetch recommendations (simulated)
  const fetchRecommendations = async () => {
    setLoadingProducts(true);
    try {
      // Simulate an API call by using a timeout
      setTimeout(() => {
        // Replace the below line with actual API fetch if available
        setProducts(dummyProducts);  // Using dummy data for now
        setShowRecommendations(true);
        toast.success("Here are your luxury product recommendations!");
      }, 2000); // Simulate a 2-second delay for loading
    } catch (error) {
      toast.error("Failed to fetch product recommendations.");
      console.error("❌ Error fetching products", error);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleAddToFavorites = async (product: any) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/users/favorites`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: product.name,
          link: product.url,
          image: product.image,
          price: product.price,
        }),
      });

      if (res.ok) {
        toast.success('Added to Favorites!');
      } else {
        toast.error('Product added to Favorites');
      }
    } catch (error) {
      toast.error('Error adding to Favorites');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-green-800">
      <header className="container mx-auto px-4 py-6 flex justify-between items-center">
        {/* Back to Home link */}
        <Link to="/" className="flex items-center space-x-2 text-white hover:text-teal-300 transition-colors">
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </Link>

        {/* Favorites link */}
        <Link
          to="/favorites"
          className="flex items-center space-x-2 text-white hover:text-teal-400 transition font-semibold"
        >
          <Heart className="w-5 h-5" />
          <span>Favorites</span>
        </Link>
      </header>

      <section className="container mx-auto px-4 py-12 text-center">
        <motion.div initial={{ x: -30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 1 }}>
          <ShoppingCart className="w-16 h-16 text-teal-400 mx-auto mb-4" />
        </motion.div>
        <h1 className="text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-blue-500 mb-4">
          MARKETPLACE
        </h1>
      </section>

      <section className="container mx-auto px-4 pb-20">
        <Card className="max-w-4xl mx-auto bg-white/10 backdrop-blur-lg border-white/20">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white mb-2">Select Product Information</CardTitle>
            <p className="text-gray-300">Fill out fields to get product recommendations</p>
          </CardHeader>

          <CardContent className="space-y-8">
            {/* Category Selection */}
            <div className="space-y-3 max-w-xs mx-auto">
              <Label className="text-white font-medium">Product Category</Label>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="bg-white/10 border-white/20 text-white">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Button to fetch product recommendations */}
            <Button
              onClick={fetchRecommendations}
              disabled={loadingProducts}
              className="w-full bg-gradient-to-r from-teal-500 to-green-500 hover:from-teal-600 hover:to-green-600 text-white py-6 text-lg font-medium"
            >
              {loadingProducts ? (
                <div className="flex items-center space-x-2 justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Loading...</span>
                </div>
              ) : (
                <>
                  <PackageSearch className="w-5 h-5 mr-2" />
                  Discover Matched Products
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Display recommendations */}
        {showRecommendations && (
          <div className="max-w-4xl mx-auto mt-12 space-y-6">
            <Card className="bg-white/10 backdrop-blur-lg border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Product Recommendations</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {products.map((product, index) => (
                    <Card key={index} className="bg-white/20 backdrop-blur-md border-white/30 p-4 hover:scale-[1.02] transition-transform">
                      <img src={product.image} alt={product.name} className="w-full h-48 object-cover rounded-md" />
                      <div className="text-center space-y-2 mt-4">
                        <h3 className="text-white text-lg font-semibold">{product.name}</h3>
                        <p className="text-gray-300">${product.price}</p>
                        <div className="flex justify-center gap-4">
                          <Button onClick={() => handleAddToFavorites(product)} className="bg-teal-500 text-white text-sm py-2 px-4 rounded-md">
                            Add to Favorites
                          </Button>
                          <Link to={product.link} className="text-teal-500 text-sm">View Details</Link>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </section>
    </div>
  );
};

export default MarketPlace;


