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
  Shield,
  Trash2,
  MessageCircle,
  Bot,
  X,
  Check,
  Loader2,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

// Import statements for better type handling
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
} 
import { productService, aiService, type Product } from '@/lib/api';

// Component for structured AI messages
const AssistantMessage = ({ content }: { content: string }) => {
  const [expanded, setExpanded] = useState(false);
  
  // Handle undefined or null content
  if (!content) {
    return <div className="p-3 text-sm text-gray-500">No response</div>;
  }
  
  const maxLength = 200;
  const needsTruncation = content.length > maxLength;
  
  const displayContent = needsTruncation && !expanded 
    ? content.substring(0, maxLength) + '...'
    : content;

  // Parse content for better structure
  const formatContent = (text: string) => {
    // Handle empty text
    if (!text || !text.trim()) {
      return <p className="text-sm text-gray-500">Empty response</p>;
    }
    
    // Split by newlines for paragraphs
    const paragraphs = text.split('\n').filter(p => p.trim());
    
    return (
      <div className="space-y-2">
        {paragraphs.map((para, idx) => {
          // Check if it's a list item
          if (para.trim().startsWith('•') || para.trim().startsWith('-') || para.trim().match(/^\d+\./)) {
            return (
              <div key={idx} className="flex gap-2">
                <span className="text-blue-500 mt-0.5">•</span>
                <span className="text-sm text-gray-700">{para.replace(/^[•\-\d+\.]\s*/, '')}</span>
              </div>
            );
          }
          // Regular paragraph
          return (
            <p key={idx} className="text-sm text-gray-700 leading-relaxed">
              {para}
            </p>
          );
        })}
      </div>
    );
  };

  return (
    <div className="p-3">
      {formatContent(displayContent)}
      {needsTruncation && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-blue-500 hover:text-blue-600 mt-2 flex items-center gap-1"
        >
          {expanded ? (
            <>
              Show less
              <ChevronUp className="w-3 h-3" />
            </>
          ) : (
            <>
              Show more
              <ChevronDown className="w-3 h-3" />
            </>
          )}
        </button>
      )}
    </div>
  );
};

// Quick action buttons for chat
const QuickActions = ({ onSelect }: { onSelect: (text: string) => void | Promise<void> }) => {
  const actions = [
    'Tell me about this product',
    'Is this available?',
    'What are similar products?',
    'Can you recommend alternatives?'
  ];

  return (
    <div className="flex flex-wrap gap-2 p-3 border-t border-gray-100">
      {actions.map((action, idx) => (
        <button
          key={idx}
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onSelect(action);
          }}
          className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
        >
          {action}
        </button>
      ))}
    </div>
  );
};

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
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedProductForChat, setSelectedProductForChat] = useState<Product | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

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

  const handleDeleteProduct = async (productId: string) => {
    try {
      await productService.deleteProduct(productId);
      toast.success('Product deleted successfully');
      setDeleteConfirmId(null);
      fetchProducts(); // Refresh the product list
    } catch (error) {
      toast.error('Failed to delete product');
      console.error('Delete error:', error);
      setDeleteConfirmId(null);
    }
  };

  const handleChatWithProduct = (product: Product) => {
    setSelectedProductForChat(product);
    setChatOpen(true);
    // Add initial message about the product
    setChatMessages([
      { 
        role: 'assistant', 
        content: `Hi! I can help you with information about "${product.name}". What would you like to know?` 
      }
    ]);
  };

  const sendChatMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;
    
    const userMessage = chatInput;
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);
    
    try {
      // Prepare context with product information if available
      const context: any = {};
      if (selectedProductForChat) {
        context.product = {
          id: selectedProductForChat.id,
          name: selectedProductForChat.name,
          price: selectedProductForChat.price,
          description: selectedProductForChat.description,
          category_id: selectedProductForChat.category_id,
          brand: selectedProductForChat.brand,
          condition: selectedProductForChat.condition,
          is_featured: selectedProductForChat.is_featured
        };
        context.interaction_type = 'product_details';
      }
      
      // Call the actual AI service
      const response = await aiService.sendMessage({
        message: userMessage,
        conversation_id: conversationId || undefined,
        context: Object.keys(context).length > 0 ? context : undefined,
        interaction_type: context.interaction_type || 'general_chat'
      } as any);
      
      // Update conversation ID if this is the first message
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      
      // Add AI response to messages
      console.log('AI Response:', response); // Debug log
      const aiContent = response?.response || response?.message || response?.content || 'No response received';
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: aiContent
      }]);
      
    } catch (error: any) {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }]);
    } finally {
      setChatLoading(false);
    }
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
                              {categories.find(c => c.value === product.category_id)?.name || 'General'}
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
                              <Button className="w-full bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white" size="sm">
                                View
                              </Button>
                            </Link>
                            <Button 
                              size="icon"
                              variant="outline"
                              onClick={() => handleChatWithProduct(product)}
                              className="hover:bg-purple-50 hover:text-purple-600"
                              title="Chat about this product"
                            >
                              <MessageCircle className="h-4 w-4" />
                            </Button>
                            <Button 
                              size="icon"
                              variant="outline"
                              onClick={() => handleAddToFavorites(product)}
                              className="hover:bg-red-50 hover:text-red-600"
                            >
                              <Heart className="h-4 w-4" />
                            </Button>
                            {deleteConfirmId === product.id ? (
                              <div className="flex gap-1">
                                <Button 
                                  size="icon"
                                  variant="ghost"
                                  onClick={() => handleDeleteProduct(product.id)}
                                  className="bg-red-50 text-red-600 hover:bg-red-100 h-8 w-8"
                                  title="Confirm delete"
                                >
                                  <Check className="h-3 w-3" />
                                </Button>
                                <Button 
                                  size="icon"
                                  variant="ghost"
                                  onClick={() => setDeleteConfirmId(null)}
                                  className="hover:bg-gray-100 h-8 w-8"
                                  title="Cancel"
                                >
                                  <X className="h-3 w-3" />
                                </Button>
                              </div>
                            ) : (
                              <Button 
                                size="icon"
                                variant="outline"
                                onClick={() => setDeleteConfirmId(product.id)}
                                className="hover:bg-red-50 hover:text-red-600"
                                title="Delete product"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            )}
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

      {/* Floating AI Chat Button */}
      <motion.button
        type="button"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setChatOpen(!chatOpen);
        }}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all"
      >
        <Bot className="h-6 w-6" />
      </motion.button>

      {/* AI Chat Popup */}
      {chatOpen && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] bg-white rounded-2xl shadow-2xl overflow-hidden"
        >
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-purple-500 to-indigo-500 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Bot className="h-6 w-6" />
              <div>
                <h3 className="font-semibold">AI Shopping Assistant</h3>
                {selectedProductForChat && (
                  <p className="text-xs opacity-90">Discussing: {selectedProductForChat.name}</p>
                )}
              </div>
            </div>
            <button
              onClick={() => {
                setChatOpen(false);
                setSelectedProductForChat(null);
                setChatMessages([]);
              }}
              className="hover:bg-white/20 rounded-full p-1"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Chat Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Bot className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>Hi! I'm your AI shopping assistant.</p>
                <p className="text-sm mt-2">Ask me anything about our products!</p>
              </div>
            ) : (
              <>
                {chatMessages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[80%] rounded-xl ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white p-3' 
                        : 'bg-white shadow-md'
                    }`}>
                      {msg.role === 'assistant' ? (
                        <AssistantMessage content={msg.content} />
                      ) : (
                        <p className="text-sm">{msg.content}</p>
                      )}
                    </div>
                  </motion.div>
                ))}
                {chatLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className="bg-white text-gray-800 shadow-md p-3 rounded-xl">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </>
            )}
          </div>

          {/* Selected Product Display */}
          {selectedProductForChat && (
            <div className="p-3 bg-white border-t flex items-center gap-3">
              <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                {selectedProductForChat.images && selectedProductForChat.images[0] ? (
                  <img 
                    src={selectedProductForChat.images[0].url} 
                    alt={selectedProductForChat.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ShoppingBag className="h-6 w-6 text-gray-400" />
                  </div>
                )}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-sm">{selectedProductForChat.name}</p>
                <p className="text-lg font-bold text-blue-600">${selectedProductForChat.price}</p>
              </div>
              <button
                onClick={() => setSelectedProductForChat(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Quick Actions */}
          {chatMessages.length === 0 && !selectedProductForChat && (
            <QuickActions onSelect={async (text) => {
              // Set the input and send directly
              setChatInput(text);
              
              // Send the message directly
              const userMessage = text;
              setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
              setChatLoading(true);
              
              try {
                const response = await aiService.sendMessage({
                  message: userMessage,
                  conversation_id: conversationId || undefined
                });
                
                if (!conversationId && response.conversation_id) {
                  setConversationId(response.conversation_id);
                }
                
                setChatMessages(prev => [...prev, { 
                  role: 'assistant', 
                  content: response.response
                }]);
              } catch (error) {
                console.error('Chat error:', error);
                setChatMessages(prev => [...prev, { 
                  role: 'assistant', 
                  content: 'Sorry, I encountered an error. Please try again.' 
                }]);
              } finally {
                setChatLoading(false);
                setChatInput('');
              }
            }} />
          )}

          {/* Chat Input */}
          <div className="p-4 bg-white border-t">
            <form onSubmit={(e) => { 
              e.preventDefault(); 
              e.stopPropagation();
              sendChatMessage(); 
              return false;
            }} className="flex gap-2">
              <Input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1"
              />
              <Button 
                type="submit"
                disabled={chatLoading || !chatInput.trim()}
                className="bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white disabled:opacity-50"
              >
                {chatLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Send'
                )}
              </Button>
            </form>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Marketplace;