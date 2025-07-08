
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ArrowLeft, Heart, ShoppingCart, CreditCard, Diamond, Gem, BadgeDollarSign } from 'lucide-react';
import { motion } from "framer-motion";

interface Seller {
  id: number;
  name: string;
  location: string;
  rating: number;
  reviews: number;
  price: number;
  shipping: string;
  verified: boolean;
  stock: number;
}

interface Product {
  id: number;
  name: string;
  brand: string;
  price: number;
  originalPrice: number;
  image: string;
  category: string;
  description: string;
  features: string[];
  availability: string;
  rating: number;
  reviews: number;
  sizes?: string[];
  colors?: string[];
}

const ProductDetail = () => {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState('');
  const [sellers, setSellers] = useState<Seller[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock product data (in a real app, this would come from an API)
  const mockProducts: Product[] = [
    {
      id: 1,
      name: "Nike Air Jordan 1 Retro High",
      brand: "Nike",
      price: 170,
      originalPrice: 200,
      image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&h=300&fit=crop",
      category: "shoes",
      description: "The iconic Air Jordan 1 in its original high-top form",
      features: ["Premium Leather", "Air Cushioning", "Rubber Outsole", "Classic Design"],
      availability: "In Stock",
      rating: 4.8,
      reviews: 1543,
      sizes: ["7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "11.5", "12"],
      colors: ["Black/Red", "White/Black", "Royal Blue", "Chicago"]
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
      features: ["Boost Technology", "Primeknit Upper", "Continental Rubber", "Energy Return"],
      availability: "Limited Stock",
      rating: 4.7,
      reviews: 892,
      sizes: ["6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10", "10.5", "11", "12"],
      colors: ["Core Black", "White", "Solar Yellow", "Collegiate Navy"]
    }
  ];

  // Mock sellers data
  const generateSellers = (productPrice: number): Seller[] => [
    {
      id: 1,
      name: "Nike Official Store",
      location: "New York, USA",
      rating: 4.9,
      reviews: 15420,
      price: productPrice,
      shipping: "Free 2-day shipping",
      verified: true,
      stock: 25
    },
    {
      id: 2,
      name: "Foot Locker",
      location: "California, USA",
      rating: 4.7,
      reviews: 8932,
      price: productPrice + 10,
      shipping: "Free shipping over $50",
      verified: true,
      stock: 12
    },
    {
      id: 3,
      name: "Sneaker Palace",
      location: "London, UK",
      rating: 4.8,
      reviews: 3421,
      price: productPrice + 25,
      shipping: "$15 international",
      verified: true,
      stock: 8
    },
    {
      id: 4,
      name: "Urban Kicks",
      location: "Tokyo, Japan",
      rating: 4.6,
      reviews: 2156,
      price: productPrice + 35,
      shipping: "$20 international",
      verified: true,
      stock: 5
    },
    {
      id: 5,
      name: "Street Style Store",
      location: "Berlin, Germany",
      rating: 4.5,
      reviews: 1893,
      price: productPrice + 15,
      shipping: "€12 EU shipping",
      verified: false,
      stock: 15
    }
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const foundProduct = mockProducts.find(p => p.id === parseInt(id || '1'));
      if (foundProduct) {
        setProduct(foundProduct);
        setSellers(generateSellers(foundProduct.price));
      }
      setLoading(false);
    }, 1000);
  }, [id]);

  const handleAddToCart = (seller: Seller) => {
    if (!selectedSize) {
      toast.error("Please select a size first");
      return;
    }
    toast.success(`Added to cart from ${seller.name}`);
  };

  const handleBuyNow = (seller: Seller) => {
    if (!selectedSize) {
      toast.error("Please select a size first");
      return;
    }
    toast.success(`Proceeding to checkout with ${seller.name}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading product details...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-white text-2xl font-bold mb-4">Product Not Found</h1>
          <Link to="/marketplace" className="text-blue-400 hover:text-blue-300">
            Return to Marketplace
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 border-b border-white/10">
        <Link to="/marketplace" className="flex items-center space-x-2 text-white hover:text-blue-300 transition-colors">
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to Marketplace</span>
        </Link>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Product Header */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <img 
              src={product.image} 
              alt={product.name}
              className="w-full h-96 object-cover rounded-2xl shadow-2xl"
            />
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="space-y-6"
          >
            <div>
              <p className="text-blue-400 text-lg font-medium">{product.brand}</p>
              <h1 className="text-4xl font-bold text-white mb-4">{product.name}</h1>
              <p className="text-gray-300 text-lg">{product.description}</p>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className={`text-lg ${i < Math.floor(product.rating) ? 'text-yellow-400' : 'text-gray-500'}`}>
                    ★
                  </span>
                ))}
              </div>
              <span className="text-gray-400">({product.reviews} reviews)</span>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-3xl font-bold text-white">${product.price}</span>
              {product.originalPrice > product.price && (
                <span className="text-gray-400 line-through text-xl">${product.originalPrice}</span>
              )}
            </div>

            <div className="flex flex-wrap gap-2">
              {product.features.map((feature, index) => (
                <Badge key={index} variant="secondary" className="bg-blue-600/20 text-blue-300">
                  {feature}
                </Badge>
              ))}
            </div>

            {/* Size Selection */}
            {product.sizes && (
              <div className="space-y-3">
                <label className="text-white font-medium text-lg">Select Size</label>
                <Select value={selectedSize} onValueChange={setSelectedSize}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Choose your size" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-white/20">
                    {product.sizes.map(size => (
                      <SelectItem key={size} value={size} className="text-white hover:bg-white/10">
                        US {size}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Color Selection */}
            {product.colors && (
              <div className="space-y-3">
                <label className="text-white font-medium text-lg">Select Color</label>
                <Select value={selectedColor} onValueChange={setSelectedColor}>
                  <SelectTrigger className="bg-white/10 border-white/20 text-white">
                    <SelectValue placeholder="Choose color" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-white/20">
                    {product.colors.map(color => (
                      <SelectItem key={color} value={color} className="text-white hover:bg-white/10">
                        {color}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </motion.div>
        </div>

        {/* Global Sellers Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Card className="bg-white/5 backdrop-blur-xl border-white/10">
            <CardHeader className="border-b border-white/10">
              <CardTitle className="text-white text-2xl flex items-center space-x-3">
                <Diamond className="w-6 h-6 text-blue-400" />
                <span>Global Sellers</span>
                {selectedSize && (
                  <Badge className="bg-blue-600 text-white">Size {selectedSize} Selected</Badge>
                )}
              </CardTitle>
              <p className="text-gray-300">
                {sellers.length} verified sellers have this item {selectedSize ? `in size ${selectedSize}` : 'available'}
              </p>
            </CardHeader>

            <CardContent className="p-6">
              <div className="space-y-4">
                {sellers.map((seller) => (
                  <Card key={seller.id} className="bg-white/10 backdrop-blur-md border-white/20">
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <h3 className="text-white font-bold text-lg">{seller.name}</h3>
                            {seller.verified && (
                              <Badge className="bg-green-600 text-white flex items-center space-x-1">
                                <Diamond className="w-3 h-3" />
                                <span>Verified</span>
                              </Badge>
                            )}
                          </div>
                          
                          <p className="text-gray-300 mb-2">{seller.location}</p>
                          
                          <div className="flex items-center space-x-4 mb-3">
                            <div className="flex items-center space-x-1">
                              {[...Array(5)].map((_, i) => (
                                <span key={i} className={`text-sm ${i < Math.floor(seller.rating) ? 'text-yellow-400' : 'text-gray-500'}`}>
                                  ★
                                </span>
                              ))}
                              <span className="text-gray-400 text-sm ml-1">({seller.reviews})</span>
                            </div>
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-300">{seller.stock} in stock</span>
                          </div>
                          
                          <p className="text-blue-300 text-sm">{seller.shipping}</p>
                        </div>

                        <div className="text-right space-y-4">
                          <div>
                            <span className="text-2xl font-bold text-white">${seller.price}</span>
                          </div>
                          
                          <div className="flex space-x-2">
                            <Button
                              onClick={() => handleAddToCart(seller)}
                              variant="outline"
                              className="border-white/20 text-white hover:bg-white/10"
                              disabled={!selectedSize}
                            >
                              <ShoppingCart className="w-4 h-4 mr-2" />
                              Add to Cart
                            </Button>
                            
                            <Button
                              onClick={() => handleBuyNow(seller)}
                              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                              disabled={!selectedSize}
                            >
                              <CreditCard className="w-4 h-4 mr-2" />
                              Buy Now
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default ProductDetail;
