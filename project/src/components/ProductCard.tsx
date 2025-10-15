import { ShoppingCart } from 'lucide-react';
import { Product } from '../lib/api';
import { formatCurrency } from '../lib/formatters';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onViewDetails: (product: Product) => void;
}

export default function ProductCard({ product, onAddToCart, onViewDetails }: ProductCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden transition-all hover:shadow-md border border-gray-200 hover:border-[#96BF48]">
      <div
        className="h-64 bg-gray-100 cursor-pointer overflow-hidden"
        onClick={() => onViewDetails(product)}
      >
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover transition-transform hover:scale-105"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = `https://via.placeholder.com/400x400/f8f9fa/6c757d?text=${encodeURIComponent(product.name)}`;
          }}
        />
      </div>
      <div className="p-4">
        <div className="mb-2">
          <span className="text-xs font-semibold text-[#96BF48] uppercase tracking-wide">
            {product.category}
          </span>
        </div>
        <h3
          className="text-lg font-semibold text-[#243746] mb-2 cursor-pointer hover:text-[#96BF48] line-clamp-2 transition-colors"
          onClick={() => onViewDetails(product)}
        >
          {product.name}
        </h3>
        <div className="flex items-center gap-3 mb-3">
          {product.color && (
            <span className="text-sm text-gray-600">Color: {product.color}</span>
          )}
          {product.size && (
            <span className="text-sm text-gray-600">Size: {product.size}</span>
          )}
        </div>
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-[#243746]">
            {formatCurrency(product.price)}
          </span>
          <button
            onClick={() => onAddToCart(product)}
            className="flex items-center gap-2 bg-[#96BF48] text-white px-4 py-2 rounded-lg hover:bg-[#85a840] transition-colors shadow-sm hover:shadow-md"
          >
            <ShoppingCart size={18} />
            <span>Add</span>
          </button>
        </div>
      </div>
    </div>
  );
}
