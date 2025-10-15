import { X, Trash2, ShoppingBag, Plus, Minus } from 'lucide-react';
import { CartItem } from '../lib/api';
import { formatCurrency } from '../lib/formatters';

interface ShoppingCartProps {
  cart: CartItem[];
  total: number;
  onClose: () => void;
  onUpdateQuantity: (productId: string, quantity: number) => void;
  onRemoveItem: (productId: string) => void;
  onCheckout: () => void;
  onClearCart: () => void;
}

export default function ShoppingCart({
  cart,
  total,
  onClose,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
  onClearCart,
}: ShoppingCartProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-end z-50">
      <div className="bg-white h-full w-full max-w-md flex flex-col shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-white">
          <div className="flex items-center gap-3">
            <ShoppingBag size={24} className="text-[#96BF48]" />
            <h2 className="text-2xl font-bold text-[#243746]">Shopping Cart</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors text-gray-700"
          >
            <X size={24} />
          </button>
        </div>

        {cart.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
            <ShoppingBag size={80} className="text-gray-300 mb-4" />
            <h3 className="text-xl font-semibold text-[#243746] mb-2">Your cart is empty</h3>
            <p className="text-gray-600 mb-6">Add some products to get started!</p>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-[#96BF48] text-white rounded-lg hover:bg-[#85a840] transition-all font-medium shadow-sm hover:shadow-md"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {cart.map((item) => (
                <div
                  key={item.product.id}
                  className="flex gap-4 bg-gray-50 rounded-lg p-4 transition-all hover:shadow-md border border-gray-200"
                >
                  <div className="w-24 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                    <img
                      src={item.product.image_url}
                      alt={item.product.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = `https://via.placeholder.com/200x200/f8f9fa/6c757d?text=${encodeURIComponent(item.product.name)}`;
                      }}
                    />
                  </div>

                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-[#243746] mb-1 line-clamp-2">
                      {item.product.name}
                    </h3>
                    <div className="flex items-center gap-2 text-xs text-gray-600 mb-2">
                      {item.product.color && <span>{item.product.color}</span>}
                      {item.product.size && (
                        <>
                          <span>•</span>
                          <span>{item.product.size}</span>
                        </>
                      )}
                    </div>
                    <p className="font-bold text-[#243746]">
                      {formatCurrency(item.product.price)}
                    </p>

                    <div className="flex items-center gap-2 mt-3">
                      <button
                        onClick={() => onUpdateQuantity(item.product.id, item.quantity - 1)}
                        className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 transition-colors text-gray-700"
                      >
                        <Minus size={16} />
                      </button>
                      <span className="w-8 text-center font-medium text-[#243746]">{item.quantity}</span>
                      <button
                        onClick={() => onUpdateQuantity(item.product.id, item.quantity + 1)}
                        className="w-8 h-8 flex items-center justify-center border border-gray-300 rounded hover:bg-gray-100 transition-colors text-gray-700"
                      >
                        <Plus size={16} />
                      </button>
                      <button
                        onClick={() => onRemoveItem(item.product.id)}
                        className="ml-auto p-2 text-gray-600 hover:bg-gray-100 rounded transition-colors"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-200 p-6 space-y-4 bg-white">
              <button
                onClick={onClearCart}
                className="w-full text-sm text-gray-600 hover:text-gray-800 font-medium hover:bg-gray-100 py-2 rounded-lg transition-colors"
              >
                Clear Cart
              </button>

              <div className="flex items-center justify-between text-lg">
                <span className="font-semibold text-[#243746]">Total:</span>
                <span className="text-2xl font-bold text-[#243746]">
                  {formatCurrency(total)}
                </span>
              </div>

              <button
                onClick={onCheckout}
                className="w-full bg-[#96BF48] text-white px-6 py-4 rounded-lg hover:bg-[#85a840] transition-all text-lg font-semibold shadow-sm hover:shadow-md"
              >
                Proceed to Checkout
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
