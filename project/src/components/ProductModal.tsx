import { X, ShoppingCart, Package } from 'lucide-react';
import { Product } from '../lib/api';
import { formatCurrency } from '../lib/formatters';
import { useState } from 'react';

interface ProductModalProps {
  product: Product;
  onClose: () => void;
  onAddToCart: (product: Product, quantity: number) => void;
}

export default function ProductModal({ product, onClose, onAddToCart }: ProductModalProps) {
  const [quantity, setQuantity] = useState(1);

  const handleAddToCart = () => {
    onAddToCart(product, quantity);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-[#243746]">Product Details</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-700"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = `https://via.placeholder.com/600x600/f8f9fa/6c757d?text=${encodeURIComponent(product.name)}`;
                }}
              />
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Package size={18} />
              <span>Product Code: {product.product_code}</span>
            </div>
          </div>

          <div className="space-y-6">
            <div>
              <span className="inline-block px-3 py-1 bg-[#96BF48] bg-opacity-10 text-[#96BF48] text-sm font-semibold rounded-full mb-3">
                {product.category}
              </span>
              <h1 className="text-3xl font-bold text-[#243746] mb-4">{product.name}</h1>
              <p className="text-4xl font-bold text-[#243746] mb-6">
                {formatCurrency(product.price)}
              </p>
            </div>

            <div className="border-t border-b border-gray-200 py-4 space-y-3">
              {product.color && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Color:</span>
                  <span className="font-medium text-[#243746]">{product.color}</span>
                </div>
              )}
              {product.size && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Size:</span>
                  <span className="font-medium text-[#243746]">{product.size}</span>
                </div>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold text-[#243746] mb-2">Description</h3>
              <p className="text-gray-600 leading-relaxed">{product.description}</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#243746] mb-2">
                  Quantity
                </label>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    className="w-10 h-10 flex items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                  >
                    -
                  </button>
                  <input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-20 text-center border border-gray-300 rounded-lg py-2 text-[#243746] focus:outline-none focus:ring-2 focus:ring-[#96BF48] focus:border-transparent"
                  />
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    className="w-10 h-10 flex items-center justify-center border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-700"
                  >
                    +
                  </button>
                </div>
              </div>

              <button
                onClick={handleAddToCart}
                className="w-full flex items-center justify-center gap-3 bg-[#96BF48] text-white px-6 py-4 rounded-lg hover:bg-[#85a840] transition-all text-lg font-semibold shadow-sm hover:shadow-md"
              >
                <ShoppingCart size={24} />
                <span>Add to Cart - {formatCurrency(product.price * quantity)}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}