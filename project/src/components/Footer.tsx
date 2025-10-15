import { Store, Mail, Phone, MapPin, Facebook, Twitter, Instagram, Linkedin, Github } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-[#243746] text-white pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          
          {/* Company Info */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <img
                src="https://cdn.shopify.com/static/shopify-favicon.png"
                alt="Shopify Logo"
                className="h-10 w-auto"
              />
              <h3 className="text-xl font-bold text-white"><i>
                Shopify
              </i></h3>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed mb-4">
              Your premium destination for quality products. Shop with confidence using our AI-powered voice assistant.
            </p>
            <div className="flex gap-3">
              <a href="#" className="w-9 h-9 bg-gray-700 hover:bg-[#96BF48] rounded-lg flex items-center justify-center transition-colors">
                <Facebook size={18} />
              </a>
              <a href="#" className="w-9 h-9 bg-gray-700 hover:bg-[#96BF48] rounded-lg flex items-center justify-center transition-colors">
                <Twitter size={18} />
              </a>
              <a href="#" className="w-9 h-9 bg-gray-700 hover:bg-[#96BF48] rounded-lg flex items-center justify-center transition-colors">
                <Instagram size={18} />
              </a>
              <a href="#" className="w-9 h-9 bg-gray-700 hover:bg-[#96BF48] rounded-lg flex items-center justify-center transition-colors">
                <Linkedin size={18} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-[#96BF48]">Quick Links</h4>
            <ul className="space-y-3">
              {["About Us", "Products", "Deals & Offers", "Contact Us", "Blog"].map((link, index) => (
                <li key={index}>
                  <a
                    href="#"
                    className="text-gray-400 hover:text-[#96BF48] transition-colors text-sm flex items-center group"
                  >
                    <span className="w-0 group-hover:w-2 h-px bg-[#96BF48] transition-all mr-0 group-hover:mr-2"></span>
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Customer Service */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-[#96BF48]">Customer Service</h4>
            <ul className="space-y-3">
              {["My Account", "Order Tracking", "Shipping & Returns", "FAQ", "Help Center"].map((link, index) => (
                <li key={index}>
                  <a
                    href="#"
                    className="text-gray-400 hover:text-[#96BF48] transition-colors text-sm flex items-center group"
                  >
                    <span className="w-0 group-hover:w-2 h-px bg-[#96BF48] transition-all mr-0 group-hover:mr-2"></span>
                    {link}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-[#96BF48]">Get In Touch</h4>
            <ul className="space-y-4">
              <li className="flex items-start gap-3">
                <MapPin size={18} className="text-[#96BF48] mt-0.5 flex-shrink-0" />
                <span className="text-gray-400 text-sm">
                  123 Commerce Street<br />
                  New York, NY 10001<br />
                  United States
                </span>
              </li>
              <li className="flex items-center gap-3">
                <Phone size={18} className="text-[#96BF48] flex-shrink-0" />
                <a
                  href="tel:+1234567890"
                  className="text-gray-400 hover:text-[#96BF48] transition-colors text-sm"
                >
                  +1 (234) 567-890
                </a>
              </li>
              <li className="flex items-center gap-3">
                <Mail size={18} className="text-[#96BF48] flex-shrink-0" />
                <a
                  href="mailto:support@shopify.com"
                  className="text-gray-400 hover:text-[#96BF48] transition-colors text-sm"
                >
                  support@shopify.com
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Newsletter Section */}
        <div className="border-t border-gray-700 pt-8 mb-8">
          <div className="max-w-xl mx-auto text-center">
            <h4 className="text-lg font-semibold mb-2 text-[#96BF48]">Subscribe to Our Newsletter</h4>
            <p className="text-gray-400 text-sm mb-4">Get the latest updates on new products and upcoming sales</p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="Enter your email address"
                className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-[#96BF48] focus:ring-1 focus:ring-[#96BF48] text-white placeholder-gray-500 text-sm"
              />
              <button className="px-6 py-3 bg-[#96BF48] text-white rounded-lg hover:bg-[#85a840] transition-all font-medium text-sm shadow-sm">
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-sm">
              © {currentYear} Shopify. All rights reserved.
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              {["Privacy Policy", "Terms of Service", "Cookie Policy", "Accessibility"].map((item, index) => (
                <a
                  key={index}
                  href="#"
                  className="text-gray-400 hover:text-[#96BF48] transition-colors text-sm"
                >
                  {item}
                </a>
              ))}
            </div>
            <div className="flex items-center gap-2 text-gray-400 text-sm">
              <span>Powered by</span>
              <a
                href="#"
                className="text-[#96BF48] hover:text-[#85a840] transition-colors font-medium flex items-center gap-1"
              >
                <Github size={16} />
                OpenAI
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
