import React, { useState, useEffect } from 'react';
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Link } from "react-router-dom";
import { 
  ArrowLeft, 
  Heart, 
  Search, 
  ShoppingBag, 
  Plus, 
  Filter,
  Star,
  Sparkles,
  Store,
  Shield
} from 'lucide-react'; 
import { productService, type Product } from '@/lib/api';

const Marketplace = () => {
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [priceRange, setPriceRange] = useState('');
  const [loadingProducts, setLoadingProducts] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [favoriteCount, setFavoriteCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const categories = [
    { name: "Sneakers & Shoes", value: "shoes", icon: "👟", color: "from-blue-400 to-indigo-400" },
    { name: "Luxury Watches", value: "watches", icon: "⌚", color: "from-purple-400 to-pink-400" },
    { name: "Designer Fragrances", value: "fragrances", icon: "🌸", color: "from-pink-400 to-rose-400" },
    { name: "High Fashion", value: "fashion", icon: "👗", color: "from-indigo-400 to-purple-400" },
    { name: "Premium Jewelry", value: "jewelry", icon: "💎", color: "from-cyan-400 to-blue-400" },
    { name: "Designer Bags", value: "bags", icon: "👜", color: "from-amber-400 to-orange-400" },
    { name: "Fine Art", value: "art", icon: "🎨", color: "from-green-400 to-teal-400" },
    { name: "Electronics", value: "electronics", icon: "📱", color: "from-slate-400 to-gray-400" }
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
    { name: "Gucci", value: "gucci" },
    { name: "Prada", value: "prada" }
  ];

  const priceRanges = [
    { name: "Under $500", value: "0-500" },
    { name: "$500 - $1K", value: "500-1000" },
    { name: "$1K - $5K", value: "1000-5000" },
    { name: "$5K - $10K", value: "5000-10000" },
    { name: "$10K - $50K", value: "10000-50000" },
    { name: "Above $50K", value: "50000+" }
  ];

  // Mock data with proper images array structure
  const mockProducts: Product[] = [
    {
      id: "1",
      name: "Nike Air Jordan 1 Retro High",
      brand: "Nike",
      price: 170,
      compare_at_price: 200,
      description: "The iconic Air Jordan 1 in its original high-top form",
      category_id: "shoes",
      quantity: 10,
      status: "active" as const,
      condition: "new" as const,
      is_featured: true,
      images: [
        {
          id: "1-1",
          url: "https://images.unsplash.com/photo-1556906781-9a412961c28c?w=400&h=400&fit=crop",
          alt_text: "Nike Air Jordan 1 Retro High",
          position: 1
        }
      ],
      tags: ["Premium Leather", "Air Cushioning", "Rubber Outsole"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: "2",
      name: "Rolex Submariner Date",
      brand: "Rolex",
      price: 11000,
      compare_at_price: 12500,
      description: "The legendary diving watch with timeless design",
      category_id: "watches",
      quantity: 3,
      status: "active" as const,
      condition: "new" as const,
      is_featured: true,
      images: [
        {
          id: "2-1",
          url: "https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=400&h=400&fit=crop",
          alt_text: "Rolex Submariner Date",
          position: 1
        }
      ],
      tags: ["Oyster Case", "Cerachrom Bezel", "300m Water Resistant"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: "3",
      name: "Hermès Birkin 35",
      brand: "Hermès",
      price: 25000,
      compare_at_price: 30000,
      description: "The most coveted handbag in the world",
      category_id: "bags",
      quantity: 1,
      status: "active" as const,
      condition: "new" as const,
      is_featured: true,
      images: [
        {
          id: "3-1",
          url: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop",
          alt_text: "Hermès Birkin 35",
          position: 1
        }
      ],
      tags: ["Togo Leather", "Handcrafted", "Palladium Hardware"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: "4",
      name: "Chanel No. 5 Parfum",
      brand: "Chanel",
      price: 350,
      compare_at_price: 400,
      description: "The timeless fragrance that defines elegance",
      category_id: "fragrances",
      quantity: 15,
      status: "active" as const,
      condition: "new" as const,
      is_featured: true,
      images: [
        {
          id: "4-1",
          url: "https://images.unsplash.com/photo-1541643600914-78b084683601?w=400&h=400&fit=crop",
          alt_text: "Chanel No. 5 Parfum",
          position: 1
        }
      ],
      tags: ["Floral", "Aldehydic", "100ml"],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

  // Fetch products from backend
  const fetchProducts = async () => {
    setLoadingProducts(true);
    try {
      const filters: any = {
        page: currentPage,
        limit: 12,
        status: 'active'
      };

      if (searchQuery) filters.search = searchQuery;
      if (selectedCategory && selectedCategory !== 'all') filters.category_id = selectedCategory;
      if (selectedBrand && selectedBrand !== 'all') filters.brand = selectedBrand;

      if (priceRange && priceRange !== 'all') {
        const [min, max] = priceRange.split('-');
        filters.min_price = parseInt(min);
        if (max && max !== '+') {
          filters.max_price = parseInt(max);
        }
      }

      const response = await productService.getProducts(filters);
      setProducts(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      setProducts(mockProducts);
    } finally {
      setLoadingProducts(false);
    }
  };

  useEffect(() => {
    const loadInitialProducts = async () => {
      setLoadingProducts(true);
      try {
        // Try to fetch from backend first
        const response = await productService.getProducts({
          limit: 12,
          page: 1
        });
        if (response.items && response.items.length > 0) {
          console.log('Setting products from API:', response.items);
          setProducts(response.items);
          setTotalPages(response.pages);
        } else {
          // Fall back to mock data if no products from backend
          console.log('No products from API, using mock data');
          setProducts(mockProducts);
        }
      } catch (error) {
        console.error('Failed to fetch products:', error);
        // Fall back to mock data on error
        setProducts(mockProducts);
      } finally {
        setLoadingProducts(false);
      }
    };

    loadInitialProducts();
  }, []);

  useEffect(() => {
    // Only fetch when filters change (not on initial load)
    if ((selectedCategory && selectedCategory !== 'all') || 
        (selectedBrand && selectedBrand !== 'all') || 
        (priceRange && priceRange !== 'all') || 
        searchQuery) {
      fetchProducts();
    }
  }, [selectedCategory, selectedBrand, priceRange, searchQuery, currentPage]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchProducts();
  };

  const handleAddToFavorites = (product: Product) => {
    setFavoriteCount(prev => prev + 1);
    toast.success(`${product.name} added to favorites!`);
  };

  const clearFilters = () => {
    setSelectedCategory('all');
    setSelectedBrand('all');
    setPriceRange('all');
    setSearchQuery('');
    setCurrentPage(1);
  };

  const getDiscountPercentage = (price: number, comparePrice?: number) => {
    if (!comparePrice || comparePrice <= price) return 0;
    return Math.round(((comparePrice - price) / comparePrice) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-100 to-purple-200">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/">
                <Button variant="ghost" size="icon" className="hover:bg-blue-50">
                  <ArrowLeft className="h-5 w-5" />
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center shadow-md">
                  <Store className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">Luxury Marketplace</h1>
                  <p className="text-sm text-gray-600">Discover authentic luxury</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Link to="/product/create">
                <Button className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white shadow-md">
                  <Plus className="mr-2 h-4 w-4" />
                  <span className="hidden sm:inline">Sell Product</span>
                </Button>
              </Link>
              <Link to="/favorites">
                <Button variant="outline" className="relative border-gray-300 hover:bg-gray-50">
                  <Heart className="mr-2 h-4 w-4" />
                  <span className="hidden sm:inline">Favorites</span>
                  {favoriteCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full h-5 w-5 flex items-center justify-center text-xs">
                      {favoriteCount}
                    </span>
                  )}
                </Button>
              </Link>
              <Button variant="outline" className="border-gray-300 hover:bg-gray-50">
                <ShoppingBag className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Cart</span>
              </Button>
              
              {/* Mobile Filter Toggle */}
              <Button 
                variant="outline" 
                size="icon"
                className="lg:hidden"
                onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
              >
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <aside className={`lg:w-64 space-y-6 ${mobileFiltersOpen ? 'block' : 'hidden lg:block'}`}>
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-800">Filters</h3>
                {(selectedCategory !== 'all' || selectedBrand !== 'all' || priceRange !== 'all') && (
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={clearFilters}
                    className="text-blue-600 hover:text-blue-700"
                  >
                    Clear all
                  </Button>
                )}
              </div>

              {/* Search */}
              <form onSubmit={handleSearch} className="mb-6">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 bg-gray-50 border-gray-200"
                  />
                </div>
              </form>

              {/* Category Filter */}
              <div className="space-y-2">
                <Label className="text-gray-700">Category</Label>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="bg-gray-50 border-gray-200">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        <span className="flex items-center gap-2">
                          <span>{category.icon}</span>
                          <span>{category.name}</span>
                        </span>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Brand Filter */}
              <div className="space-y-2">
                <Label className="text-gray-700">Brand</Label>
                <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                  <SelectTrigger className="bg-gray-50 border-gray-200">
                    <SelectValue placeholder="All brands" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All brands</SelectItem>
                    {luxuryBrands.map((brand) => (
                      <SelectItem key={brand.value} value={brand.value}>
                        {brand.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Price Range Filter */}
              <div className="space-y-2">
                <Label className="text-gray-700">Price Range</Label>
                <Select value={priceRange} onValueChange={setPriceRange}>
                  <SelectTrigger className="bg-gray-50 border-gray-200">
                    <SelectValue placeholder="Any price" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Any price</SelectItem>
                    {priceRanges.map((range) => (
                      <SelectItem key={range.value} value={range.value}>
                        {range.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </motion.div>

            {/* Quick Stats */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-gray-800">Market Insights</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Active Listings</span>
                  <span className="font-semibold text-gray-800">{products.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Avg. Discount</span>
                  <span className="font-semibold text-green-600">15%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">New Today</span>
                  <span className="font-semibold text-blue-600">12</span>
                </div>
              </div>
            </motion.div>
          </aside>

          {/* Products Grid */}
          <div className="flex-1">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-800">
                  {selectedCategory ? categories.find(c => c.value === selectedCategory)?.name : 'All Products'}
                </h2>
                <p className="text-gray-600 mt-1">
                  {products.length} {products.length === 1 ? 'result' : 'results'} found
                </p>
              </div>
              
              <Select defaultValue="featured">
                <SelectTrigger className="w-[180px] bg-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="featured">Featured</SelectItem>
                  <SelectItem value="price-low">Price: Low to High</SelectItem>
                  <SelectItem value="price-high">Price: High to Low</SelectItem>
                  <SelectItem value="newest">Newest First</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Products Grid */}
            {loadingProducts ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
              </div>
            ) : products.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-16 bg-white/60 backdrop-blur-xl rounded-2xl"
              >
                <Search className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No products found</h3>
                <p className="text-gray-500">Try adjusting your filters or search query</p>
              </motion.div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product, index) => (
                  <motion.div
                    key={product.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    whileHover={{ y: -5 }}
                  >
                    <Card className="bg-white/80 backdrop-blur-xl border-white/40 shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden h-full">
                      <div className="relative">
                        {/* Product Image */}
                        <div className="relative h-64 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden">
                          {product.images && product.images[0] ? (
                            <img 
                              src={product.images[0].url} 
                              alt={product.images[0].alt_text || product.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <ShoppingBag className="h-20 w-20 text-gray-400" />
                            </div>
                          )}
                          
                          {/* Discount Badge */}
                          {product.compare_at_price && product.compare_at_price > product.price && (
                            <div className="absolute top-3 left-3">
                              <Badge className="bg-red-500 text-white border-0">
                                -{getDiscountPercentage(product.price, product.compare_at_price)}%
                              </Badge>
                            </div>
                          )}
                          
                          {/* Featured Badge */}
                          {product.is_featured && (
                            <div className="absolute top-3 right-3">
                              <Badge className="bg-gradient-to-r from-amber-400 to-orange-400 text-white border-0">
                                <Star className="w-3 h-3 mr-1" />
                                Featured
                              </Badge>
                            </div>
                          )}

                          {/* Quick Actions */}
                          <div className="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button 
                              size="icon"
                              variant="secondary"
                              className="bg-white/90 backdrop-blur-sm"
                              onClick={() => handleAddToFavorites(product)}
                            >
                              <Heart className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        <CardContent className="p-5">
                          {/* Brand & Category */}
                          <div className="flex items-center gap-2 mb-2">
                            {product.brand && (
                              <Badge variant="secondary" className="text-xs">
                                {product.brand}
                              </Badge>
                            )}
                            <Badge variant="outline" className="text-xs">
                              {categories.find(c => c.value === product.category_id)?.icon || '📦'}
                            </Badge>
                          </div>

                          {/* Product Name */}
                          <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2 min-h-[3rem]">
                            {product.name}
                          </h3>

                          {/* Price */}
                          <div className="flex items-baseline gap-2 mb-3">
                            <span className="text-2xl font-bold text-gray-900">
                              ${product.price.toLocaleString()}
                            </span>
                            {product.compare_at_price && product.compare_at_price > product.price && (
                              <span className="text-sm text-gray-500 line-through">
                                ${product.compare_at_price.toLocaleString()}
                              </span>
                            )}
                          </div>

                          {/* Stock Status */}
                          <div className="flex items-center gap-4 mb-4 text-sm">
                            <div className="flex items-center gap-1">
                              {product.quantity > 0 ? (
                                <>
                                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                                  <span className="text-gray-600">In Stock</span>
                                </>
                              ) : (
                                <>
                                  <div className="w-2 h-2 bg-red-500 rounded-full" />
                                  <span className="text-gray-600">Out of Stock</span>
                                </>
                              )}
                            </div>
                            {product.condition && (
                              <div className="flex items-center gap-1">
                                <Shield className="w-3 h-3 text-blue-600" />
                                <span className="text-gray-600 capitalize">{product.condition}</span>
                              </div>
                            )}
                          </div>

                          {/* Action Buttons */}
                          <div className="flex gap-2">
                            <Link to={`/product/${product.id}`} className="flex-1">
                              <Button className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white">
                                View Details
                              </Button>
                            </Link>
                            <Button 
                              size="icon"
                              variant="outline"
                              onClick={() => handleAddToFavorites(product)}
                            >
                              <Heart className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex justify-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  Previous
                </Button>
                <div className="flex items-center gap-2">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => (
                    <Button
                      key={i + 1}
                      variant={currentPage === i + 1 ? "default" : "outline"}
                      size="icon"
                      onClick={() => setCurrentPage(i + 1)}
                    >
                      {i + 1}
                    </Button>
                  ))}
                </div>
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;