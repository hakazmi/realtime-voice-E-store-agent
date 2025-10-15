import { useState, useEffect } from 'react';
import { api, Product, CartItem, OrderCustomer, OrderResponse } from './lib/api';
import { sessionManager } from './lib/session';
import Header from './components/Header';
import ProductGrid from './components/ProductGrid';
import ProductModal from './components/ProductModal';
import ShoppingCart from './components/ShoppingCart';
import Checkout from './components/Checkout';
import OrderConfirmation from './components/OrderConfirmation';
import VoiceAssistant from './components/VoiceAssistant';
import Footer from './components/Footer';

function App() {
  const [sessionId] = useState(() => sessionManager.getSessionId());
  const [cart, setCart] = useState<CartItem[]>([]);
  const [cartTotal, setCartTotal] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [orderConfirmation, setOrderConfirmation] = useState<OrderResponse | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    loadCart();
  }, [sessionId]);

  const loadCart = async () => {
    try {
      const cartData = await api.getCart(sessionId);
      setCart(cartData.cart);
      setCartTotal(cartData.total);
    } catch (error) {
      console.error('Failed to load cart:', error);
    }
  };

  const handleCartUpdate = () => {
    console.log('🔄 Cart updated from voice assistant, refreshing...');
    loadCart();
  };

  const handleProductClick = async (productId: string) => {
    console.log('🔍 Product clicked from voice assistant:', productId);
    
    try {
      const product = await api.getProduct(productId);
      setSelectedProduct(product);
    } catch (error) {
      console.error('Failed to load product details:', error);
      alert('Failed to load product details');
    }
  };

  const handleAddToCart = async (product: Product, quantity: number = 1) => {
    try {
      await api.addToCart(sessionId, product.id, quantity);
      await loadCart();
    } catch (error) {
      console.error('Failed to add to cart:', error);
      alert('Failed to add item to cart');
    }
  };

  const handleUpdateQuantity = async (productId: string, quantity: number) => {
    if (quantity < 1) {
      await handleRemoveFromCart(productId);
      return;
    }

    try {
      await api.updateCartQuantity(sessionId, productId, quantity);
      await loadCart();
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  };

  const handleRemoveFromCart = async (productId: string) => {
    try {
      await api.removeFromCart(sessionId, productId);
      await loadCart();
    } catch (error) {
      console.error('Failed to remove from cart:', error);
    }
  };

  const handleClearCart = async () => {
    if (!confirm('Are you sure you want to clear your cart?')) return;

    try {
      await api.clearCart(sessionId);
      await loadCart();
    } catch (error) {
      console.error('Failed to clear cart:', error);
    }
  };

  const handlePlaceOrder = async (customer: OrderCustomer) => {
    try {
      const items = cart.map((item) => ({
        pricebook_entry_id: item.product.pricebook_entry_id,
        quantity: item.quantity,
      }));

      const orderResponse = await api.placeOrder(customer, items);
      setOrderConfirmation(orderResponse);
      setShowCheckout(false);
      setShowCart(false);
      await api.clearCart(sessionId);
      await loadCart();
    } catch (error) {
      console.error('Failed to place order:', error);
      alert('Failed to place order. Please try again.');
    }
  };

  const cartItemCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="min-h-screen bg-white">
      <Header 
        cartItemCount={cartItemCount} 
        onCartClick={() => setShowCart(true)}
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        <ProductGrid
          onAddToCart={(product) => handleAddToCart(product, 1)}
          onViewDetails={setSelectedProduct}
        />
      </main>

      {selectedProduct && (
        <ProductModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onAddToCart={handleAddToCart}
        />
      )}

      {showCart && (
        <ShoppingCart
          cart={cart}
          total={cartTotal}
          onClose={() => setShowCart(false)}
          onUpdateQuantity={handleUpdateQuantity}
          onRemoveItem={handleRemoveFromCart}
          onCheckout={() => {
            setShowCart(false);
            setShowCheckout(true);
          }}
          onClearCart={handleClearCart}
        />
      )}

      {showCheckout && (
        <Checkout
          cart={cart}
          total={cartTotal}
          onClose={() => setShowCheckout(false)}
          onPlaceOrder={handlePlaceOrder}
        />
      )}

      {orderConfirmation && (
        <OrderConfirmation
          order={orderConfirmation}
          onClose={() => setOrderConfirmation(null)}
        />
      )}

      <VoiceAssistant 
        sessionId={sessionId}
        onCartUpdate={handleCartUpdate}
        onProductClick={handleProductClick}
      />

      <Footer />
    </div>
  );
}

export default App;