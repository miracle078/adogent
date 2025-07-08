
import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { ArrowLeft, Heart, PackageSearch, Diamond, ShoppingCart, CreditCard, BadgeDollarSign, Gift, Gem } from 'lucide-react'; 
import { motion } from "framer-motion";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

const Marketplace = () => {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [priceRange, setPriceRange] = useState('');
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [favoriteCount, setFavoriteCount] = useState(0);

  const categories = [
    { name: "Sneakers & Shoes", value: "shoes", icon: "👟" },
    { name: "Luxury Watches", value: "watches", icon: "⌚" },
    { name: "Designer Fragrances", value: "fragrances", icon: "🌸" },
    { name: "High Fashion", value: "fashion", icon: "👗" },
    { name: "Premium Jewelry", value: "jewelry", icon: "💎" },
    { name: "Luxury Cars", value: "cars", icon: "🚗" },
    { name: "Fine Art", value: "art", icon: "🎨" },
    { name: "Real Estate", value: "realestate", icon: "🏛️" },
    { name: "Luxury Travel", value: "travel", icon: "✈️" }
  ];

  const luxuryBrands = [
    { name: "Nike", value: "nike" },
    { name: "Adidas", value: "adidas" },
    { name: "Jordan", value: "jordan" },
    { name: "Rolex", value: "rolex" },
    { name: "Cartier", value: "cartier" },
    { name: "Hermès", value: "hermes" },
    { name: "Louis Vuitton", value: "lv" },
    { name: "Chanel", value: "chanel" },
    { name: "Tiffany & Co.", value: "tiffany" },
    { name: "Rolls-Royce", value: "rollsroyce" },
    { name: "Ferrari", value: "ferrari" }
  ];

  const priceRanges = [
    { name: "Under $500", value: "0-500" },
    { name: "$500 - $1K", value: "500-1000" },
    { name: "$1K - $5K", value: "1000-5000" },
    { name: "$5K - $10K", value: "5000-10000" },
    { name: "$10K - $50K", value: "10000-50000" },
    { name: "$50K - $100K", value: "50000-100000" },
    { name: "$100K - $500K", value: "100000-500000" },
    { name: "$500K - $1M", value: "500000-1000000" },
    { name: "Above $1M", value: "1000000+" }
  ];

  // Enhanced products data with shoes and luxury items
  const luxuryProducts = [
    {
      id: 1,
      name: "Nike Air Jordan 1 Retro High",
      brand: "Nike",
      price: 170,
      originalPrice: 200,
      image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=300&fit=crop",
      category: "shoes",
      description: "The iconic Air Jordan 1 in its original high-top form",
      features: ["Premium Leather", "Air Cushioning", "Rubber Outsole"],
      availability: "In Stock",
      rating: 4.8,
      reviews: 1543
    },
    {
      id: 2,
      name: "Adidas Ultraboost 22",
      brand: "Adidas",
      price: 190,
      originalPrice: 220,
      image: "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&h=300&fit=crop",
      category: "shoes",
      description: "Revolutionary running shoe with responsive Boost midsole",
      features: ["Boost Technology", "Primeknit Upper", "Continental Rubber"],
      availability: "Limited Stock",
      rating: 4.7,
      reviews: 892
    },
    {
      id: 3,
      name: "Rolls-Royce Phantom VIII",
      brand: "Rolls-Royce",
      price: 450000,
      originalPrice: 500000,
      image: "https://images.unsplash.com/photo-1563720223185-11003d516935?w=500&h=300&fit=crop",
      category: "cars",
      description: "The pinnacle of luxury motoring with bespoke craftsmanship",
      features: ["Handcrafted Interior", "V12 Engine", "Starlight Headliner"],
      availability: "Limited Edition",
      rating: 5.0,
      reviews: 24
    },
    {
      id: 4,
      name: "Patek Philippe Nautilus",
      brand: "Patek Philippe",
      price: 85000,
      originalPrice: 90000,
      image: "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=500&h=300&fit=crop",
      category: "watches",
      description: "Iconic luxury timepiece with exceptional craftsmanship",
      features: ["Swiss Movement", "18K Gold", "Water Resistant"],
      availability: "In Stock",
      rating: 4.9,
      reviews: 156
    },
    {
      id: 5,
      name: "Hermès Birkin 35",
      brand: "Hermès",
      price: 35000,
      originalPrice: 40000,
      image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=500&h=300&fit=crop",
      category: "fashion",
      description: "The most coveted handbag in the world",
      features: ["Crocodile Leather", "Hand-Stitched", "Palladium Hardware"],
      availability: "Waitlist Only",
      rating: 5.0,
      reviews: 89
    },
    {
      id: 6,
      name: "Tiffany Yellow Diamond Necklace",
      brand: "Tiffany & Co.",
      price: 125000,
      originalPrice: 150000,
      image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=500&h=300&fit=crop",
      category: "jewelry",
      description: "Exquisite yellow diamond set in platinum",
      features: ["5 Carat Diamond", "Platinum Setting", "Certified Authentic"],
      availability: "Exclusive",
      rating: 5.0,
      reviews: 45
    }
  ];

  const fetchRecommendations = async () => {
    setLoadingProducts(true);
    try {
      setTimeout(() => {
        let filteredProducts = luxuryProducts;
        
        if (selectedCategory) {
          filteredProducts = filteredProducts.filter(p => p.category === selectedCategory);
        }
        
        if (selectedBrand) {
          filteredProducts = filteredProducts.filter(p => 
            p.brand.toLowerCase().includes(selectedBrand.toLowerCase())
          );
        }
        
        if (searchQuery) {
          filteredProducts = filteredProducts.filter(p => 
            p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.description.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }
        
        setProducts(filteredProducts);
        setShowRecommendations(true);
        toast.success("Curated luxury selections just for you!");
      }, 2000);
    } catch (error) {
      toast.error("Failed to fetch luxury recommendations.");
      console.error("❌ Error fetching products", error);
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleAddToWishlist = async (product: any) => {
    try {
      setFavoriteCount(prev => prev + 1);
      toast.success(`${product.name} added to your luxury wishlist!`);
    } catch (error) {
      toast.error('Error adding to wishlist');
    }
  };

  const handleQuickPurchase = (product: any) => {
    toast.success(`Initiating luxury concierge service for ${product.name}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Premium Header */}
      <header className="container mx-auto px-4 py-6 border-b border-white/10">
        <div className="flex justify-between items-center">
          <Link to="/" className="flex items-center space-x-2 text-white hover:text-blue-300 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Return Home</span>
          </Link>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-blue-300">
              <Diamond className="w-5 h-5" />
              <span className="font-medium">Premium Member</span>
            </div>
            
            <Link to="/wishlist" className="flex items-center space-x-2 text-white hover:text-blue-400 transition relative">
              <Heart className="w-5 h-5" />
              <span>Wishlist</span>
              {favoriteCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                  {favoriteCount}
                </span>
              )}
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <motion.div 
          initial={{ y: -30, opacity: 0 }} 
          animate={{ y: 0, opacity: 1 }} 
          transition={{ duration: 1 }}
          className="mb-8"
        >
          <div className="flex justify-center items-center space-x-4 mb-6">
            <Diamond className="w-12 h-12 text-blue-400" />
            <Gem className="w-16 h-16 text-blue-300" />
            <Diamond className="w-12 h-12 text-blue-400" />
          </div>
        </motion.div>
        
        <h1 className="text-6xl lg:text-8xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-400 to-blue-500 mb-6">
          LUXURY MARKETPLACE
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
          Discover the world's most exclusive luxury goods, curated by experts and available to discerning collectors
        </p>
      </section>

      {/* Filters & Search */}
      <section className="container mx-auto px-4 pb-12">
        <Card className="max-w-6xl mx-auto bg-white/5 backdrop-blur-xl border-white/10">
          <CardHeader className="text-center border-b border-white/10">
            <CardTitle className="text-3xl text-white mb-2 flex items-center justify-center space-x-3">
              <Gift className="w-8 h-8 text-blue-400" />
              <span>Luxury Concierge</span>
            </CardTitle>
            <p className="text-gray-300">Tell us your preferences and we'll curate the perfect selection</p>
          </CardHeader>

          <CardContent className="p-8">
            {/* Search Bar */}
            <div className="mb-8">
              <Label className="text-white font-medium mb-3 block">Search Luxury Items</Label>
              <Input
                placeholder="Search for luxury watches, jewelry, cars, shoes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-white/10 border-white/20 text-white placeholder:text-gray-400 text-lg py-3"
              />
            </div>

            {/* Filter Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="space-y-3">
                <Label className="text-white font-medium">Category</Label>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-white/20">
                    {categories.map(cat => (
                      <SelectItem key={cat.value} value={cat.value} className="text-white hover:bg-white/10">
                        <span className="flex items-center space-x-2">
                          <span>{cat.icon}</span>
                          <span>{cat.name}</span>
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label className="text-white font-medium">Luxury Brand</Label>
                <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Select brand" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-white/20">
                    {luxuryBrands.map(brand => (
                      <SelectItem key={brand.value} value={brand.value} className="text-white hover:bg-white/10">
                        {brand.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label className="text-white font-medium">Price Range</Label>
                <Select value={priceRange} onValueChange={setPriceRange}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Select range" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-white/20">
                    {priceRanges.map(range => (
                      <SelectItem key={range.value} value={range.value} className="text-white hover:bg-white/10">
                        {range.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Action Button */}
            <Button
              onClick={fetchRecommendations}
              disabled={loadingProducts}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 text-lg font-medium rounded-xl"
            >
              {loadingProducts ? (
                <div className="flex items-center space-x-3 justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                  <span>Curating luxury selections...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <PackageSearch className="w-6 h-6" />
                  <span>Discover Luxury Collections</span>
                </div>
              )}
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Luxury Product Grid */}
      {showRecommendations && (
        <section className="container mx-auto px-4 pb-20">
          <div className="max-w-7xl mx-auto">
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
              <CardHeader className="border-b border-white/10">
                <CardTitle className="text-white text-2xl flex items-center space-x-3">
                  <Gem className="w-6 h-6 text-blue-400" />
                  <span>Curated Luxury Selection</span>
                </CardTitle>
                <p className="text-gray-300">
                  {products.length} exclusive items matched to your preferences
                </p>
              </CardHeader>
              
              <CardContent className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {products.map((product) => (
                    <motion.div
                      key={product.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 }}
                    >
                      <Link to={`/product/${product.id}`}>
                        <Card className="bg-white/10 backdrop-blur-md border-white/20 overflow-hidden hover:scale-[1.02] transition-all duration-300 group cursor-pointer">
                          <div className="relative">
                            <img 
                              src={product.image} 
                              alt={product.name} 
                              className="w-full h-56 object-cover group-hover:scale-105 transition-transform duration-300" 
                            />
                            <div className="absolute top-4 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                              {product.availability}
                            </div>
                            {product.originalPrice > product.price && (
                              <div className="absolute top-4 left-4 bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                                Save ${(product.originalPrice - product.price).toLocaleString()}
                              </div>
                            )}
                          </div>
                          
                          <CardContent className="p-6 space-y-4">
                            <div>
                              <p className="text-blue-400 text-sm font-medium">{product.brand}</p>
                              <h3 className="text-white text-xl font-bold">{product.name}</h3>
                              <p className="text-gray-300 text-sm mt-2">{product.description}</p>
                            </div>

                            <div className="flex items-center space-x-1">
                              {[...Array(5)].map((_, i) => (
                                <span key={i} className={`text-sm ${i < Math.floor(product.rating) ? 'text-yellow-400' : 'text-gray-500'}`}>
                                  ★
                                </span>
                              ))}
                              <span className="text-gray-400 text-sm ml-2">({product.reviews} reviews)</span>
                            </div>

                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="text-2xl font-bold text-white">
                                  ${product.price.toLocaleString()}
                                </span>
                                {product.originalPrice > product.price && (
                                  <span className="text-gray-400 line-through text-lg">
                                    ${product.originalPrice.toLocaleString()}
                                  </span>
                                )}
                              </div>
                            </div>

                            <div className="flex flex-wrap gap-2 mb-4">
                              {product.features.map((feature: string, index: number) => (
                                <span key={index} className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded-md text-xs">
                                  {feature}
                                </span>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                      
                      {/* Action buttons outside the link */}
                      <div className="flex space-x-3 mt-4 px-6">
                        <Button 
                          onClick={(e) => {
                            e.preventDefault();
                            handleAddToWishlist(product);
                          }}
                          variant="outline"
                          className="flex-1 border-white/20 text-white hover:bg-white/10"
                        >
                          <Heart className="w-4 h-4 mr-2" />
                          Wishlist
                        </Button>
                        
                        <Button 
                          onClick={(e) => {
                            e.preventDefault();
                            handleQuickPurchase(product);
                          }}
                          className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                        >
                          <CreditCard className="w-4 h-4 mr-2" />
                          Inquire
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      )}

      {/* Luxury Services Footer */}
      <footer className="border-t border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="space-y-3">
              <BadgeDollarSign className="w-12 h-12 text-blue-400 mx-auto" />
              <h3 className="text-white text-xl font-bold">Concierge Service</h3>
              <p className="text-gray-300">Personal luxury shopping assistant available 24/7</p>
            </div>
            
            <div className="space-y-3">
              <CreditCard className="w-12 h-12 text-blue-400 mx-auto" />
              <h3 className="text-white text-xl font-bold">Flexible Payment</h3>
              <p className="text-gray-300">Private financing and payment plans available</p>
            </div>
            
            <div className="space-y-3">
              <Diamond className="w-12 h-12 text-blue-400 mx-auto" />
              <h3 className="text-white text-xl font-bold">Authentication</h3>
              <p className="text-gray-300">Every item verified by luxury goods experts</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Marketplace;
