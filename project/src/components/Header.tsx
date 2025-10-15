import { ShoppingBag, Menu, User, Heart, X } from 'lucide-react';

interface HeaderProps {
  cartItemCount: number;
  onCartClick: () => void;
  onMenuClick: () => void;
  sidebarOpen: boolean;
}

export default function Header({
  cartItemCount,
  onCartClick,
  onMenuClick,
  sidebarOpen,
}: HeaderProps) {
  return (
    <>
      <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 shadow-sm z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Left Section: Menu and Logo */}
            <div className="flex items-center gap-6">
              {/* Mobile Menu Button */}
              <button
                onClick={onMenuClick}
                className="lg:hidden p-2 hover:bg-gray-50 rounded-lg transition-colors text-gray-700"
                aria-label="Open menu"
              >
                <Menu size={24} />
              </button>

              {/* Desktop Menu Button */}
              <button
                onClick={onMenuClick}
                className="hidden lg:flex items-center gap-2 p-2 hover:bg-gray-50 rounded-lg transition-colors text-gray-700"
                aria-label="Open menu"
              >
                <Menu size={20} />
                <span className="text-sm font-medium">Menu</span>
              </button>

              {/* ✅ Official Shopify Logo */}
              <div className="flex items-center gap-3 flex-shrink-0">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Shopify_logo_2018.svg"
                  alt="Shopify Logo"
                  className="h-7 w-auto"
                />
              </div>

              {/* Desktop Navigation */}
              <nav className="hidden lg:flex items-center gap-1">
                <a
                  href="#"
                  className="px-3 py-2 text-sm text-gray-700 hover:text-[#96BF48] hover:bg-gray-50 rounded-lg transition-colors font-medium"
                >
                  Products
                </a>
                <a
                  href="#"
                  className="px-3 py-2 text-sm text-gray-700 hover:text-[#96BF48] hover:bg-gray-50 rounded-lg transition-colors font-medium"
                >
                  Deals
                </a>
                <a
                  href="#"
                  className="px-3 py-2 text-sm text-gray-700 hover:text-[#96BF48] hover:bg-gray-50 rounded-lg transition-colors font-medium"
                >
                  About
                </a>
                <a
                  href="#"
                  className="px-3 py-2 text-sm text-gray-700 hover:text-[#96BF48] hover:bg-gray-50 rounded-lg transition-colors font-medium"
                >
                  Contact
                </a>
              </nav>
            </div>

            {/* Right Section: Actions */}
            <div className="flex items-center gap-2 sm:gap-4">
              {/* Wishlist */}
              <button
                className="hidden sm:flex p-2 hover:bg-gray-50 rounded-lg transition-colors text-gray-700"
                aria-label="Wishlist"
              >
                <Heart size={20} />
              </button>

              {/* Account */}
              <button
                className="hidden sm:flex p-2 hover:bg-gray-50 rounded-lg transition-colors text-gray-700"
                aria-label="Account"
              >
                <User size={20} />
              </button>

              {/* Cart */}
              <button
                onClick={onCartClick}
                className="relative flex items-center gap-2 px-3 sm:px-4 py-2 bg-[#96BF48] text-white rounded-lg hover:bg-[#85a840] transition-all font-medium text-sm sm:text-base shadow-sm hover:shadow-md"
                aria-label="Shopping cart"
              >
                <ShoppingBag size={20} />
                <span className="hidden sm:inline">Cart</span>
                {cartItemCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center animate-pulse shadow-sm">
                    {cartItemCount > 99 ? '99+' : cartItemCount}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ✅ Sidebar Menu */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30">
          {/* Overlay */}
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={onMenuClick}
          />

          {/* Sidebar Panel */}
          <div className="absolute left-0 top-0 h-full w-80 bg-white shadow-2xl flex flex-col">
            {/* Sidebar Header */}
            <div className="flex-shrink-0 flex items-center justify-between p-6 border-b border-gray-200 bg-white">
              <div className="flex items-center gap-3">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Shopify_logo_2018.svg"
                  alt="Shopify Logo"
                  className="h-6 w-auto"
                />
              </div>
              <button
                onClick={onMenuClick}
                className="p-2 hover:bg-gray-50 rounded-full transition-colors text-gray-700"
              >
                <X size={24} />
              </button>
            </div>

            {/* Scrollable Sidebar Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6 space-y-8">
                {/* New Arrival Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4 flex items-center gap-2">
                    <div className="w-2 h-2 bg-[#96BF48] rounded-full"></div>
                    New Arrival
                  </h3>
                  <div className="space-y-2">
                    {[
                      'Spring Collection 2024',
                      'Limited Edition',
                      'Just Landed',
                      'Summer Essentials',
                      'Back to School',
                    ].map((item) => (
                      <a
                        key={item}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {item}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Collections Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">Collections</h3>
                  <div className="space-y-2">
                    {[
                      "Men's Fashion",
                      "Women's Wear",
                      'Kids & Babies',
                      'Home & Living',
                      'Electronics',
                      'Sports & Outdoors',
                      'Beauty & Personal Care',
                    ].map((item) => (
                      <a
                        key={item}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {item}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Brands Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">Popular Brands</h3>
                  <div className="space-y-2">
                    {[
                      'Nike',
                      'Adidas',
                      'Zara',
                      'H&M',
                      'Apple',
                      'Samsung',
                      'Sony',
                      "Levi's",
                      'Puma',
                    ].map((brand) => (
                      <a
                        key={brand}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {brand}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Additional Categories */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">More Categories</h3>
                  <div className="space-y-2">
                    {[
                      'Sale & Clearance',
                      'Best Sellers',
                      'Gift Cards',
                      'Customer Favorites',
                    ].map((cat) => (
                      <a
                        key={cat}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {cat}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
