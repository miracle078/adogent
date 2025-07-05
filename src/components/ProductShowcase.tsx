import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  originalPrice?: number;
  category: string;
  image: string;
  description: string;
  rating: number;
  verified: boolean;
  aiRecommended?: boolean;
}

interface ProductShowcaseProps {
  products?: Product[];
  onProductSelect?: (product: Product) => void;
  title?: string;
}

export const ProductShowcase = ({ 
  products = [], 
  onProductSelect,
  title = "Curated Luxury Collection"
}: ProductShowcaseProps) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Sample products for demo
  const sampleProducts: Product[] = [
    {
      id: '1',
      name: 'Hermès Birkin 35',
      brand: 'Hermès',
      price: 12500,
      category: 'handbags',
      image: '/api/placeholder/300/300',
      description: 'Iconic luxury handbag in pristine condition',
      rating: 5.0,
      verified: true,
      aiRecommended: true
    },
    {
      id: '2',
      name: 'Rolex Submariner',
      brand: 'Rolex',
      price: 8500,
      originalPrice: 9200,
      category: 'watches',
      image: '/api/placeholder/300/300',
      description: 'Classic diving watch with impeccable craftsmanship',
      rating: 4.9,
      verified: true
    },
    {
      id: '3',
      name: 'Chanel Classic Flap',
      brand: 'Chanel',
      price: 6800,
      category: 'handbags',
      image: '/api/placeholder/300/300',
      description: 'Timeless quilted bag in black caviar leather',
      rating: 4.8,
      verified: true,
      aiRecommended: true
    }
  ];

  const displayProducts = products.length > 0 ? products : sampleProducts;
  const categories = ['all', ...new Set(displayProducts.map(p => p.category))];

  const filteredProducts = selectedCategory === 'all' 
    ? displayProducts 
    : displayProducts.filter(p => p.category === selectedCategory);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h2 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          {title}
        </h2>
        
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button
              key={category}
              onClick={() => setSelectedCategory(category)}
              variant={selectedCategory === category ? "luxury" : "outline"}
              size="sm"
              className="capitalize"
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <Card 
            key={product.id} 
            className="group overflow-hidden bg-gradient-card border-primary/20 shadow-elegant hover:shadow-luxury transition-luxury cursor-pointer"
            onClick={() => onProductSelect?.(product)}
          >
            <div className="relative">
              <div className="aspect-square bg-gradient-dark p-4 flex items-center justify-center">
                <div className="w-full h-full bg-muted/20 rounded-lg flex items-center justify-center">
                  <span className="text-muted-foreground text-sm">Product Image</span>
                </div>
              </div>
              
              {product.aiRecommended && (
                <Badge className="absolute top-2 left-2 bg-primary/90 text-primary-foreground shadow-glow">
                  AI Pick
                </Badge>
              )}
              
              {product.verified && (
                <Badge className="absolute top-2 right-2 bg-accent/90 text-accent-foreground">
                  Verified
                </Badge>
              )}
              
              {product.originalPrice && (
                <Badge className="absolute bottom-2 right-2 bg-destructive/90 text-destructive-foreground">
                  Sale
                </Badge>
              )}
            </div>

            <div className="p-4 space-y-3">
              <div>
                <p className="text-sm text-muted-foreground font-medium">{product.brand}</p>
                <h3 className="font-semibold group-hover:text-primary transition-colors">
                  {product.name}
                </h3>
              </div>

              <p className="text-sm text-muted-foreground line-clamp-2">
                {product.description}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-lg font-bold text-primary">
                    ${product.price.toLocaleString()}
                  </span>
                  {product.originalPrice && (
                    <span className="text-sm text-muted-foreground line-through">
                      ${product.originalPrice.toLocaleString()}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-1">
                  <span className="text-sm font-medium">{product.rating}</span>
                  <div className="w-4 h-4 bg-primary/60 rounded-full" />
                </div>
              </div>

              <Button 
                variant="premium" 
                size="sm" 
                className="w-full group-hover:bg-gradient-primary group-hover:text-primary-foreground"
                onClick={(e) => {
                  e.stopPropagation();
                  onProductSelect?.(product);
                }}
              >
                View Details
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No products found in this category.</p>
        </div>
      )}
    </div>
  );
};