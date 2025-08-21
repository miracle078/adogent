import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { ArrowLeft, Heart, ShoppingCart, ShoppingBag, Star, Shield, MessageCircle, Loader2 } from 'lucide-react';
import { motion } from "framer-motion";
import { productService, type Product } from '@/lib/api/services/product.service';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) {
        setError('No product ID provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await productService.getProduct(id);
        setProduct(data);
      } catch (err) {
        console.error('Error fetching product:', err);
        setError('Failed to load product. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  const handleAddToCart = () => {
    toast.success(`Added ${product?.name} to cart`);
  };

  const handleBuyNow = () => {
    toast.success(`Proceeding to checkout for ${product?.name}`);
  };

  const handleAddToFavorites = () => {
    toast.success(`Added ${product?.name} to favorites`);
  };

  const handleStartChat = () => {
    navigate('/marketplace', { 
      state: { 
        openChat: true, 
        productForChat: product 
      } 
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">Loading product details...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-gray-800 text-2xl font-bold mb-4">
            {error || 'Product Not Found'}
          </h1>
          <Link to="/marketplace">
            <Button className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white">
              Return to Marketplace
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const currentImage = product.images && product.images[selectedImageIndex] 
    ? product.images[selectedImageIndex].url 
    : null;

  const discountPercentage = product.compare_at_price && product.compare_at_price > product.price
    ? Math.round(((product.compare_at_price - product.price) / product.compare_at_price) * 100)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <Link to="/marketplace" className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors">
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Marketplace</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Product Images */}
          <motion.div 
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-4"
          >
            {/* Main Image */}
            <div className="relative bg-white rounded-2xl shadow-lg overflow-hidden h-[500px]">
              {currentImage ? (
                <img 
                  src={currentImage} 
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-100">
                  <ShoppingBag className="h-32 w-32 text-gray-400" />
                </div>
              )}
              
              {/* Discount Badge */}
              {discountPercentage > 0 && (
                <div className="absolute top-4 left-4">
                  <Badge className="bg-red-500 text-white border-0 text-lg px-3 py-1">
                    -{discountPercentage}% OFF
                  </Badge>
                </div>
              )}

              {/* Featured Badge */}
              {product.is_featured && (
                <div className="absolute top-4 right-4">
                  <Badge className="bg-gradient-to-r from-amber-400 to-orange-400 text-white border-0">
                    <Star className="w-4 h-4 mr-1" />
                    Featured
                  </Badge>
                </div>
              )}
            </div>

            {/* Image Thumbnails */}
            {product.images && product.images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto">
                {product.images.map((image, index) => (
                  <button
                    key={image.id}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImageIndex === index ? 'border-blue-500' : 'border-gray-200'
                    }`}
                  >
                    <img 
                      src={image.url} 
                      alt={`${product.name} ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </motion.div>

          {/* Product Info */}
          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="space-y-6"
          >
            {/* Product Header */}
            <div>
              {/* Brand & Category */}
              <div className="flex items-center gap-2 mb-3">
                {product.brand && (
                  <Badge variant="secondary" className="text-sm">
                    {product.brand}
                  </Badge>
                )}
                {product.condition && (
                  <Badge variant="outline" className="text-sm">
                    <Shield className="w-3 h-3 mr-1" />
                    {product.condition}
                  </Badge>
                )}
              </div>

              {/* Product Name */}
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {product.name}
              </h1>

              {/* SKU */}
              {product.sku && (
                <p className="text-sm text-gray-500 mb-4">SKU: {product.sku}</p>
              )}

              {/* Price */}
              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-4xl font-bold text-gray-900">
                  ${product.price.toLocaleString()}
                </span>
                {product.compare_at_price && product.compare_at_price > product.price && (
                  <>
                    <span className="text-xl text-gray-500 line-through">
                      ${product.compare_at_price.toLocaleString()}
                    </span>
                    <Badge className="bg-green-100 text-green-800 border-green-200">
                      Save ${(product.compare_at_price - product.price).toFixed(2)}
                    </Badge>
                  </>
                )}
              </div>

              {/* Stock Status */}
              <div className="flex items-center gap-2 mb-4">
                {product.quantity > 0 ? (
                  <>
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span className="text-green-600 font-medium">In Stock</span>
                    <span className="text-gray-500">({product.quantity} available)</span>
                  </>
                ) : (
                  <>
                    <div className="w-2 h-2 bg-red-500 rounded-full" />
                    <span className="text-red-600 font-medium">Out of Stock</span>
                  </>
                )}
              </div>
            </div>

            {/* Description */}
            {product.description && (
              <Card className="border-gray-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{product.description}</p>
                </CardContent>
              </Card>
            )}

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-sm">
                    {tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <div className="flex gap-3">
                <Button 
                  onClick={handleBuyNow}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white"
                  size="lg"
                  disabled={product.quantity === 0}
                >
                  <ShoppingCart className="w-5 h-5 mr-2" />
                  Buy Now
                </Button>
                <Button 
                  onClick={handleAddToCart}
                  variant="outline"
                  size="lg"
                  className="flex-1"
                  disabled={product.quantity === 0}
                >
                  Add to Cart
                </Button>
              </div>
              <div className="flex gap-3">
                <Button 
                  onClick={handleAddToFavorites}
                  variant="outline"
                  size="lg"
                  className="flex-1 hover:bg-red-50 hover:text-red-600"
                >
                  <Heart className="w-5 h-5 mr-2" />
                  Add to Favorites
                </Button>
                <Button 
                  onClick={handleStartChat}
                  variant="outline"
                  size="lg"
                  className="flex-1 hover:bg-purple-50 hover:text-purple-600"
                >
                  <MessageCircle className="w-5 h-5 mr-2" />
                  Chat About This
                </Button>
              </div>
            </div>

            {/* Additional Info */}
            <Card className="border-gray-200 bg-blue-50/50">
              <CardContent className="p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Category</span>
                    <p className="font-medium text-gray-800">
                      General
                    </p>
                  </div>
                  {product.barcode && (
                    <div>
                      <span className="text-gray-500">Barcode</span>
                      <p className="font-medium text-gray-800">{product.barcode}</p>
                    </div>
                  )}
                  <div>
                    <span className="text-gray-500">Created</span>
                    <p className="font-medium text-gray-800">
                      {new Date(product.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Updated</span>
                    <p className="font-medium text-gray-800">
                      {new Date(product.updated_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;