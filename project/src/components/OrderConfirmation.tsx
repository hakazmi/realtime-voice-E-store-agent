import { CheckCircle, Package } from 'lucide-react';
import { OrderResponse } from '../lib/api';
import { formatCurrency } from '../lib/formatters';

interface OrderConfirmationProps {
  order: OrderResponse;
  onClose: () => void;
}

export default function OrderConfirmation({ order, onClose }: OrderConfirmationProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-8 text-center">
        <div className="flex justify-center mb-6">
          <CheckCircle size={80} className="text-green-500" />
        </div>

        <h2 className="text-3xl font-bold text-gray-900 mb-2">Order Placed!</h2>
        <p className="text-gray-600 mb-6">
          Thank you for your purchase. Your order has been confirmed.
        </p>

        <div className="bg-gray-50 rounded-lg p-6 mb-6 space-y-3">
          <div className="flex items-center justify-center gap-2 text-gray-700">
            <Package size={20} />
            <span className="font-medium">Order Number</span>
          </div>
          <p className="text-3xl font-bold text-blue-600">{order.order_number}</p>
          <div className="pt-3 border-t border-gray-300">
            <p className="text-sm text-gray-600 mb-1">Total Amount</p>
            <p className="text-2xl font-bold text-gray-900">
              {formatCurrency(order.total_amount)}
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-sm text-gray-600">
            A confirmation email has been sent with your order details.
          </p>
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    </div>
  );
}
