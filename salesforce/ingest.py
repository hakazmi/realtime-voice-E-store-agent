import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv
from urllib.parse import unquote, urlparse, parse_qs

# --- Load environment variables ---
load_dotenv()

# --- Connect to Salesforce ---
sf = Salesforce(
    username=os.getenv("SALESFORCE_USERNAME"),
    password=os.getenv("SALESFORCE_PASSWORD"),
    security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
    domain=os.getenv("SALESFORCE_DOMAIN", "test")  # default to sandbox
)
print("✅ Connected to Salesforce for product ingestion")

# --- Helper: Clean Google redirect URLs ---
def clean_image_url(url: str) -> str:
    """Extract the real image link from a Google redirect URL."""
    if "google.com/imgres" in url:
        query = parse_qs(urlparse(url).query)
        if "imgurl" in query:
            return unquote(query["imgurl"][0])
    return url

# --- Get Standard Pricebook ---
pricebook_query = sf.query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
pricebook_id = pricebook_query["records"][0]["Id"]
print(f"📘 Standard Pricebook ID: {pricebook_id}")

# --- Demo product catalog ---
products = [
    # ===== Belts =====
    {
        "Name": "Men's Leather Belt - Classic Black",
        "ProductCode": "BELT001",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "34-38 inches",
        "Description": "Crafted from high-quality genuine leather, this classic black belt features a polished silver buckle, adjustable fit for sizes 34-38 inches, durable stitching, and a timeless design suitable for both formal attire and casual outfits.",
        "Image_URL__c": "https://www.google.com/imgres?q=leather%20belts%20for%20men&imgurl=https%3A%2F%2Fimg.drz.lazcdn.com%2Fstatic%2Fpk%2Fp%2Fa2e687e811f612d80b34bc1e21c18576.jpg_720x720q80.jpg&imgrefurl=https%3A%2F%2Fwww.daraz.pk%2Fproducts%2Fmen-leather-belt-2-in-1-double-sided-black-and-brown-leather-belt-for-men-i350603555.html&docid=i9eYChUBd8xwEM&tbnid=8bH9zODmqQVEnM&vet=12ahUKEwiGkf2u_JiQAxVrTaQEHa--GwYQM3oECBwQAA..i&w=720&h=720&hcb=2&ved=2ahUKEwiGkf2u_JiQAxVrTaQEHa--GwYQM3oECBwQAA",
        "Price__c": 49.99
    },
    {
        "Name": "Men's Leather Belt - Brown",
        "ProductCode": "BELT002",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "34-40 inches",
        "Description": "Made from 100% genuine leather, this stylish brown belt offers an adjustable length from 34-40 inches, a classic buckle, reinforced edges for longevity, and versatile styling for everyday wear.",
        "Image_URL__c": "https://www.google.com/imgres?q=leather%20belts%20for%20men&imgurl=https%3A%2F%2Fimg.drz.lazcdn.com%2Fstatic%2Fpk%2Fp%2Fa2e687e811f612d80b34bc1e21c18576.jpg_720x720q80.jpg&imgrefurl=https%3A%2F%2Fwww.daraz.pk%2Fproducts%2Fmen-leather-belt-2-in-1-double-sided-black-and-brown-leather-belt-for-men-i350603555.html&docid=i9eYChUBd8xwEM&tbnid=8bH9zODmqQVEnM&vet=12ahUKEwiGkf2u_JiQAxVrTaQEHa--GwYQM3oECBwQAA..i&w=720&h=720&hcb=2&ved=2ahUKEwiGkf2u_JiQAxVrTaQEHa--GwYQM3oECBwQAA",
        "Price__c": 44.99
    },
    {
        "Name": "Men's Reversible Belt - Black/Brown",
        "ProductCode": "BELT003",
        "Family": "Accessories",
        "Color__c": "Black/Brown",
        "Size__c": "32-42 inches",
        "Description": "Versatile reversible belt with black on one side and brown on the other, made from genuine leather, featuring a reversible silver buckle, adjustable from 32-42 inches, perfect for matching different outfits with durable construction and smooth finish.",
        "Image_URL__c": "https://www.brooktaverner.us/media/catalog/product/cache/ac7ff1d745bed6c9eaee1b53e51b2680/1/7/1778a_belt_web_grey.jpg",
        "Price__c": 54.99
    },
    {
        "Name": "Men's Braided Belt - Navy",
        "ProductCode": "BELT004",
        "Family": "Accessories",
        "Color__c": "Navy",
        "Size__c": "32-40 inches",
        "Description": "Stylish braided navy belt made from durable elastic fabric with leather accents, adjustable fit, casual design suitable for jeans or chinos, offering flexibility and comfort for all-day wear.",
        "Image_URL__c": "https://www.avalongolf.co/wp-content/uploads/braided-golf-belt-mens-navy-blue-x.jpg",
        "Price__c": 39.99
    },
    {
        "Name": "Men's Suede Belt - Gray",
        "ProductCode": "BELT005",
        "Family": "Accessories",
        "Color__c": "Gray",
        "Size__c": "34-38 inches",
        "Description": "Soft suede gray belt with a matte finish silver buckle, comfortable and stylish, ideal for casual wear, featuring reinforced backing for durability and an adjustable length.",
        "Image_URL__c": "https://i.etsystatic.com/7453621/r/il/69bf67/1904279069/il_fullxfull.1904279069_yahr.jpg",
        "Price__c": 49.99
    },
    {
        "Name": "Men's Designer Belt - Gold Buckle",
        "ProductCode": "BELT006",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "32-40 inches",
        "Description": "Luxury designer belt with a prominent gold buckle, crafted from premium leather, elegant design for formal occasions, adjustable fit with fine stitching and high-end finish.",
        "Image_URL__c": "https://img4.dhresource.com/webp/m/0x0/f3/albu/km/l/30/f4012960-4127-4434-9877-a92b500ac7bd.jpg",
        "Price__c": 69.99
    },
    {
        "Name": "Men's Casual Belt - Green Canvas",
        "ProductCode": "BELT007",
        "Family": "Accessories",
        "Color__c": "Green",
        "Size__c": "32-42 inches",
        "Description": "Rugged green canvas belt for casual use, featuring double grommet holes for adjustment, durable metal buckle, ideal for outdoor activities or everyday casual outfits with reinforced material.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/61Zbbb-hrXL._UY1000_.jpg",
        "Price__c": 29.99
    },

    # ===== Wallets =====
    {
        "Name": "Men's Bifold Wallet - Black Leather",
        "ProductCode": "WALLET001",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "Standard",
        "Description": "This classic bifold wallet is made from premium black leather, featuring 6 card slots, a coin pocket, multiple bill compartments, RFID protection, and a slim profile for comfortable pocket carry.",
        "Image_URL__c": "https://www.google.com/imgres?q=leather%20wallets%20for%20men&imgurl=https%3A%2F%2Fwww.affordable.pk%2Fuploads%2Fproducts%2F16978076470_Sparkling-Black-Duo-Line-Leather-Wallets-for-Men-001.jpg&imgrefurl=https%3A%2F%2Fwww.affordable.pk%2Fitem%2Fmen-accessories-bags-wings-sparkling-brown-leather-wallets-for-men-wings-34096&docid=7y1kF6NnfKxV8M&tbnid=BmJC8xiPUz4OIM&vet=12ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECGgQAA..i&w=225&h=225&hcb=2&ved=2ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECGgQAA",
        "Price__c": 39.99
    },
    {
        "Name": "Men's Slim Wallet - Brown Leather",
        "ProductCode": "WALLET002",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "Slim",
        "Description": "Designed for minimalism, this slim brown leather wallet includes RFID blocking technology, several card slots, a cash compartment, and a compact size ideal for front pocket use.",
        "Image_URL__c": "https://www.google.com/imgres?q=leather%20wallets%20for%20men&imgurl=https%3A%2F%2Fhub.com.pk%2Fcdn%2Fshop%2Ffiles%2FMW0343-045_2_1200x.jpg%3Fv%3D1757147997&imgrefurl=https%3A%2F%2Fhub.com.pk%2Fcollections%2Fview-all%3Fsrsltid%3DAfmBOoraDdxm7w09WljcC8iB_PDTjvYV26cwFqIkuUpeEsBPD1Ud6i24&docid=t1vuvRNM6qChCM&tbnid=4WVckpNSrLWDEM&vet=12ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECH8QAA..i&w=1200&h=1200&hcb=2&ved=2ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECH8QAA",
        "Price__c": 34.99
    },
    {
        "Name": "Men's Travel Wallet - Blue",
        "ProductCode": "WALLET003",
        "Family": "Accessories",
        "Color__c": "Navy Blue",
        "Size__c": "Large",
        "Description": "Perfect for travelers, this large navy blue wallet features a passport holder, multiple card slots, zippered coin pocket, bill sections, made from durable material with secure closures.",
        "Image_URL__c": "https://www.google.com/imgres?q=leather%20wallets%20for%20men&imgurl=https%3A%2F%2Festreet.pk%2Fmedia%2Fcatalog%2Fproduct%2Fcache%2F12d96b7cdffbe2e82811f5f2c39a586d%2Fw%2Fa%2Fwallets-small-lover-.jpg&imgrefurl=https%3A%2F%2Festreet.pk%2Fen%2Fsmall-lover-original-leather-new-style-men-wallet-men-wallet&docid=tK5PGCcjUPiNbM&tbnid=pL4l8ciSuPrwJM&vet=12ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECEMQAA..i&w=500&h=500&hcb=2&ved=2ahUKEwj7jI-8_ZiQAxWZVaQEHXk_A6EQM3oECEMQAA",
        "Price__c": 59.99
    },
    {
        "Name": "Men's Trifold Wallet - Black Leather",
        "ProductCode": "WALLET004",
        "Family": "Accessories",
        "Color__c": "Black",
        "Size__c": "Standard",
        "Description": "Trifold black leather wallet with multiple card slots, ID window, bill compartments, RFID blocking for added security, and sturdy construction for daily use.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/71TJ09Px2TL._UY1000_.jpg",
        "Price__c": 44.99
    },
    {
        "Name": "Men's Card Holder - Brown Leather",
        "ProductCode": "WALLET005",
        "Family": "Accessories",
        "Color__c": "Brown",
        "Size__c": "Slim",
        "Description": "Slim brown leather card holder designed to hold multiple cards and folded cash, minimalist style with easy access pull tab, perfect for front pocket carry.",
        "Image_URL__c": "https://vonbaer.com/cdn/shop/files/von-baer-minimalist-best-quality-mens-slim-leather-card-holder-brown-with-cash-in-the-hands.jpg?v=1712303223&width=500",
        "Price__c": 24.99
    },
    {
        "Name": "Men's RFID Blocking Wallet - Gray",
        "ProductCode": "WALLET006",
        "Family": "Accessories",
        "Color__c": "Gray",
        "Size__c": "Standard",
        "Description": "Gray bifold wallet with advanced RFID blocking technology, multiple card slots, coin pocket, bill holder, slim yet spacious design for everyday security and convenience.",
        "Image_URL__c": "https://i.etsystatic.com/9675620/r/il/b2aa7a/3523557487/il_fullxfull.3523557487_g33m.jpg",
        "Price__c": 39.99
    },
    {
        "Name": "Men's Coin Wallet - Tan Leather",
        "ProductCode": "WALLET007",
        "Family": "Accessories",
        "Color__c": "Tan",
        "Size__c": "Compact",
        "Description": "Compact tan leather coin wallet with dual zippers, key ring attachment, space for coins, cards, and small items, durable and portable for on-the-go use.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/61c0v2pV6ML._UY1000_.jpg",
        "Price__c": 19.99
    },
    {
        "Name": "Men's Long Wallet - Blue",
        "ProductCode": "WALLET008",
        "Family": "Accessories",
        "Color__c": "Blue",
        "Size__c": "Long",
        "Description": "Spacious long blue leather wallet, ideal for holding unfolded bills, multiple cards, and documents, with elegant stitching, secure closure, and premium full-grain leather construction.",
        "Image_URL__c": "https://www.theoutlierman.com/cdn/shop/products/the-outlierman-wallets-globetrotter-full-grain-leather-long-wallet-blue-22855254048941.jpg?v=1608633489",
        "Price__c": 59.99
    },

    # ===== Shoes =====
    {
        "Name": "Men's Formal Shoes - Oxford Black",
        "ProductCode": "SHOE001",
        "Family": "Footwear",
        "Color__c": "Black",
        "Size__c": "7-11",
        "Description": "Elegant black oxford shoes crafted from fine leather, with lace-up closure, cushioned insoles for all-day comfort, durable soles, available in sizes 7-11, ideal for formal occasions like weddings or business meetings.",
        "Image_URL__c": "https://www.google.com/imgres?q=formal%20shoes%20for%20men&imgurl=http%3A%2F%2Fbnbfootwear.pk%2Fcdn%2Fshop%2Ffiles%2F88132_BLK_NEW.webp%3Fv%3D1735134851&imgrefurl=https%3A%2F%2Fbnbfootwear.pk%2Fproducts%2F88132-men-leather-formal-shoes-copy%3Fsrsltid%3DAfmBOopgQjFwV4MYnPnrek_og2laLyj8BFVhR-I1LkrtGPGGWba-cAoU&docid=rMB8LOJLYN1TeM&tbnid=5SaFsapDRryNaM&vet=12ahUKEwih5Pz9_ZiQAxVQNfsDHRM0HDMQM3oECBUQAA..i&w=713&h=713&hcb=2&ved=2ahUKEwih5Pz9_ZiQAxVQNfsDHRM0HDMQM3oECBUQAA",
        "Price__c": 89.99
    },
    {
        "Name": "Men's Casual Sneakers - White",
        "ProductCode": "SHOE002",
        "Family": "Footwear",
        "Color__c": "White",
        "Size__c": "7-12",
        "Description": "Comfortable white casual sneakers featuring breathable mesh upper, cushioned soles for support, lace-up style, lightweight construction, available in sizes 7-12, perfect for daily wear and light activities.",
        "Image_URL__c": "https://www.google.com/imgres?q=white%20casual%20sneakers%20for%20men&imgurl=https%3A%2F%2Fn.nordstrommedia.com%2Fit%2Fc6de93cc-736b-487f-adb9-269f26947b46.jpeg%3Fh%3D368%26w%3D240%26dpr%3D2&imgrefurl=https%3A%2F%2Fwww.nordstrom.com%2Fbrowse%2Fmen%2Fshoes%2Fwhite-sneakers%3FfilterByOccasion%3Dcasual%26srsltid%3DAfmBOoouULTyi_2YlriBlRlmvPZnRNN52yUzrnmHfVG1aeWSXhmAz1xD&docid=RjBCpaktOcyVdM&tbnid=auSHiM7Ajg6soM&vet=12ahUKEwjYubKa_piQAxVzNfsDHdngOWIQM3oECBkQAA..i&w=480&h=736&hcb=2&ved=2ahUKEwjYubKa_piQAxVzNfsDHdngOWIQM3oECBkQAA",
        "Price__c": 69.99
    },
    {
        "Name": "Men's Loafers - Tan",
        "ProductCode": "SHOE003",
        "Family": "Footwear",
        "Color__c": "Tan",
        "Size__c": "8-11",
        "Description": "Stylish tan loafers made from soft leather, slip-on design for convenience, flexible rubber soles, cushioned footbed, sizes 8-11, suitable for semi-formal events or office casual looks.",
        "Image_URL__c": "https://www.google.com/imgres?q=tan%20loffers%20for%20men&imgurl=https%3A%2F%2Fwww.calza.com.pk%2Fcdn%2Fshop%2Ffiles%2F2_6f47d37a-86de-4da1-992a-0040da6a8f06.jpg%3Fv%3D1756727758&imgrefurl=https%3A%2F%2Fwww.calza.com.pk%2Fproducts%2Fmens-comfy-loafers-cz-lh-0034-tan%3Fsrsltid%3DAfmBOoq3HkS4rCtGnoki6r8ivJmpIKs5gI_I0yGVEf03fqa_Y0Ek-hBm&docid=lLniFQSPGL1rnM&tbnid=xZoRoTm0Tr2iMM&vet=12ahUKEwi63c-q_piQAxUWNfsDHQRwEdcQM3oECBkQAA..i&w=1400&h=1400&hcb=2&ved=2ahUKEwi63c-q_piQAxUWNfsDHQRwEdcQM3oECBkQAA",
        "Price__c": 74.99
    },
    {
        "Name": "Men's Sports Running Shoes - Grey",
        "ProductCode": "SHOE004",
        "Family": "Footwear",
        "Color__c": "Grey",
        "Size__c": "7-12",
        "Description": "Lightweight grey sports running shoes with flexible rubber soles, enhanced ankle support, breathable mesh fabric, shock-absorbing cushioning, sizes 7-12, designed for running, jogging, and gym workouts.",
        "Image_URL__c": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.metroshoes.com%2Fmetro-48-25-grey-sports-running-shoes.html&psig=AOvVaw0EipO77pUqUFl1_iwaBfSB&ust=1760442569867000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCMjky-eNoZADFQAAAAAdAAAAABAE",
        "Price__c": 79.99
    },
    {
        "Name": "Men's Boots - Brown Leather",
        "ProductCode": "SHOE005",
        "Family": "Footwear",
        "Color__c": "Brown",
        "Size__c": "7-12",
        "Description": "Durable brown leather boots with lace-up closure, weather-resistant treatment, sturdy rubber soles, cushioned insoles for comfort, available in sizes 7-12, suitable for casual outings or work environments.",
        "Image_URL__c": "https://thursdayboots.com/cdn/shop/products/T-1024x1024-Men-Captain-Arizona-LB1.jpg?v=1569061198&width=1024",
        "Price__c": 99.99
    },
    {
        "Name": "Men's Sandals - Black",
        "ProductCode": "SHOE006",
        "Family": "Footwear",
        "Color__c": "Black",
        "Size__c": "8-11",
        "Description": "Comfortable black leather sandals with adjustable buckle straps, woven upper design, cushioned footbed, non-slip soles, sizes 8-11, ideal for summer wear or casual strolls.",
        "Image_URL__c": "https://cdn.shopify.com/s/files/1/0082/4708/3104/products/1045-Daniel-Black-01.jpg",
        "Price__c": 49.99
    },
    {
        "Name": "Men's Dress Shoes - Burgundy",
        "ProductCode": "SHOE007",
        "Family": "Footwear",
        "Color__c": "Burgundy",
        "Size__c": "7-11",
        "Description": "Sophisticated burgundy dress shoes made from polished leather, lace-up style, brogue detailing for elegance, comfortable lining, sizes 7-11, perfect for formal events or professional settings.",
        "Image_URL__c": "https://thesuitdepot.com/cdn/shop/products/ariston-shoes-ariston-mens-solid-burgundy-whole-cut-oxford-leather-dress-shoes-31490480079030.jpg?v=1727284385",
        "Price__c": 84.99
    },
    {
        "Name": "Men's Running Shoes - Blue",
        "ProductCode": "SHOE008",
        "Family": "Footwear",
        "Color__c": "Blue",
        "Size__c": "7-12",
        "Description": "Performance blue running shoes with breathable mesh upper, responsive cushioning, supportive heel counter, durable outsole, sizes 7-12, designed for long-distance running and training sessions.",
        "Image_URL__c": "https://i.ebayimg.com/images/g/ut8AAOSwlf1izYFx/s-l1200.jpg",
        "Price__c": 74.99
    },
    {
        "Name": "Men's Slippers - Gray",
        "ProductCode": "SHOE009",
        "Family": "Footwear",
        "Color__c": "Gray",
        "Size__c": "8-12",
        "Description": "Cozy gray knit slippers with memory foam padding, soft lining, anti-skid rubber sole, easy slip-on design, sizes 8-12, perfect for indoor relaxation and home use.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/81soVOfJc+L._UY900_.jpg",
        "Price__c": 29.99
    },

    # ===== Watches =====
    {
        "Name": "Men's Chronograph Watch - Silver Steel",
        "ProductCode": "WATCH001",
        "Family": "Watches",
        "Color__c": "Silver",
        "Size__c": "42mm",
        "Description": "Classic silver chronograph watch with stainless steel strap, water-resistant up to 50 meters, precise quartz movement, sub-dials for stopwatch functions, tachymeter bezel, 42mm case size for a bold look.",
        "Image_URL__c": "https://www.google.com/imgres?q=silver%20watches%20for%20men&imgurl=https%3A%2F%2Fwatchcentre.pk%2Fwp-content%2Fuploads%2F2022%2F04%2Fcurren-8364-silver-chain-analog-dial-mens-watch.jpg&imgrefurl=https%3A%2F%2Fwatchcentre.pk%2Fproduct%2Fcurren-8364-silver-chain-classic-white-dial-mens-dress-watch%2F&docid=R50YhIsvIyD2FM&tbnid=1eP-gppDVDPkEM&vet=12ahUKEwiN64HW_piQAxWuUKQEHe93D6oQM3oECBsQAA..i&w=800&h=800&hcb=2&ved=2ahUKEwiN64HW_piQAxWuUKQEHe93D6oQM3oECBsQAA",
        "Price__c": 129.99
    },
    {
        "Name": "Men's Analog Watch - Leather Strap Brown",
        "ProductCode": "WATCH002",
        "Family": "Watches",
        "Color__c": "Brown",
        "Size__c": "40mm",
        "Description": "Elegant analog watch featuring a genuine brown leather strap, crisp white dial with date window, water-resistant casing, reliable movement, 40mm diameter, versatile for casual or professional settings.",
        "Image_URL__c": "https://www.google.com/imgres?q=brown%20leather%20strap%20watch%20for%20men&imgurl=http%3A%2F%2Fdreamspakistan.com%2Fcdn%2Fshop%2Fproducts%2FFS-5380-1.jpg%3Fv%3D1756377447&imgrefurl=https%3A%2F%2Fdreamspakistan.com%2Fproducts%2Ffossil-neutra-brown-leather-strap-cream-dial-chronograph-quartz-watch-for-gents-fs5380-042-911933%3Fsrsltid%3DAfmBOorhVbtnpFAD8K5XmbqpFgVOqGF73sB7qpY6K3UHFdXggYvwXwdK&docid=d_1Lj4s1snMENM&tbnid=_lg6WC2ez70nIM&vet=12ahUKEwjF9qXw_piQAxUHUqQEHUbTKZgQM3oECBsQAA..i&w=600&h=600&hcb=2&ved=2ahUKEwjF9qXw_piQAxUHUqQEHUbTKZgQM3oECBsQAA",
        "Price__c": 99.99
    },
    {
        "Name": "Men's Digital Sports Watch - Black",
        "ProductCode": "WATCH003",
        "Family": "Watches",
        "Color__c": "Black",
        "Size__c": "45mm",
        "Description": "Black digital sports watch with water resistance up to 100 meters, stopwatch, alarm, LED backlight for low-light visibility, durable resin strap, 45mm case, ideal for active lifestyles.",
        "Image_URL__c": "https://www.google.com/imgres?q=digital%20sports%20watch%20for%20men&imgurl=https%3A%2F%2Fimg.drz.lazcdn.com%2Fstatic%2Fpk%2Fp%2F3fa6d023165f8ce1618a156d23098186.jpg_720x720q80.jpg&imgrefurl=https%3A%2F%2Fwww.daraz.pk%2Fproducts%2Fmens-digital-sports-watch-waterproof-watches-for-men-with-led-back-light-watch-for-men-i351140996.html&docid=ODKUQDFklrcKoM&tbnid=fGYiuko0ehVv_M&vet=12ahUKEwi0pq2G_5iQAxWxAvsDHb8NIuYQM3oECB0QAA..i&w=720&h=720&hcb=2&ved=2ahUKEwi0pq2G_5iQAxWxAvsDHb8NIuYQM3oECB0QAA",
        "Price__c": 79.99
    },
    {
        "Name": "Men's Smartwatch - Silver",
        "ProductCode": "WATCH004",
        "Family": "Watches",
        "Color__c": "Silver",
        "Size__c": "44mm",
        "Description": "Silver smartwatch equipped with fitness tracking, Bluetooth connectivity for notifications, heart rate monitor, step and calorie counter, 44mm touchscreen, compatible with iOS and Android devices for seamless integration.",
        "Image_URL__c": "https://www.google.com/imgres?q=silver%20smart%20watch%20for%20men&imgurl=https%3A%2F%2Fi5.walmartimages.com%2Fseo%2FLIGE-Smart-Watch-Men-for-Android-iPhone-1-39-Smart-Watches-with-Fitness-Tracker-IP67-Waterproof_0d1e9fe3-cee2-4518-bba0-5e7cfd579e11.fecf9859e6557cee56b112cafb794931.jpeg&imgrefurl=https%3A%2F%2Fwww.readytoeat.com%2F%3Fj%3D82362649011730%26srsltid%3DAfmBOormZAqunBB_8UAOorHtLnGgcJArqeIYldH4ZOFWhIhVGSnEySI1&docid=6Gs6Nj5CY7KOrM&tbnid=ALDaJ78i47qHDM&vet=12ahUKEwii5rSV_5iQAxUTUqQEHTG4Op0QM3oECB8QAA..i&w=1600&h=1600&hcb=2&itg=1&ved=2ahUKEwii5rSV_5iQAxUTUqQEHTG4Op0QM3oECB8QAA",
        "Price__c": 149.99
    },
    {
        "Name": "Men's Minimalist Watch - Blue Dial",
        "ProductCode": "WATCH005",
        "Family": "Watches",
        "Color__c": "Blue",
        "Size__c": "40mm",
        "Description": "Minimalist watch with a navy-blue dial, stainless steel mesh band for comfort, precise quartz movement, water-resistant up to 30 meters, 40mm case, offering an elegant and understated style.",
        "Image_URL__c": "https://www.google.com/imgres?q=blue%20dial%20watch%20for%20men&imgurl=https%3A%2F%2Fwatchcentre.pk%2Fwp-content%2Fuploads%2F2022%2F03%2Fmtp-v002d-2b3-casio-blue-dial-mens.jpg&imgrefurl=https%3A%2F%2Fwatchcentre.pk%2Fproduct%2Fcasio-mtp-v002d-2b3-silver-chain-analog-blue-dial-dress-watch%2F&docid=hrvQQBaeoqzjyM&tbnid=jnuUwfdCEnb-jM&vet=12ahUKEwjsrPen_5iQAxV_U6QEHdesFzsQM3oECB4QAA..i&w=600&h=600&hcb=2&ved=2ahUKEwjsrPen_5iQAxV_U6QEHdesFzsQM3oECB4QAA",
        "Price__c": 109.99
    },
    {
        "Name": "Men's Dive Watch - Black",
        "ProductCode": "WATCH006",
        "Family": "Watches",
        "Color__c": "Black",
        "Size__c": "44mm",
        "Description": "Robust black dive watch with water resistance up to 1250 meters, automatic Swiss movement, luminous markers for visibility, helium escape valve, stainless steel case and band, 44mm diameter for professional diving.",
        "Image_URL__c": "https://oceaneva.com/cdn/shop/products/oceaneva-bkiib-bkip-1000m-1250m-316l-stainless-steel-watch-automatic-watch-bgw9-swiss-superluminova-ceramic-bezel-dive-watch-sw200-1-swiss-automatic-movement-78403_1280x.jpg?v=1746248365",
        "Price__c": 199.99
    },
    {
        "Name": "Men's Automatic Watch - Silver",
        "ProductCode": "WATCH007",
        "Family": "Watches",
        "Color__c": "Silver",
        "Size__c": "40mm",
        "Description": "Silver automatic watch with self-winding mechanism, blue dial featuring date display, stainless steel bracelet, water-resistant, 40mm case, combining reliability and classic style for everyday use.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/41JB1+RYr4L._UY900_.jpg",
        "Price__c": 129.99
    },
    {
        "Name": "Men's Leather Band Watch - Black",
        "ProductCode": "WATCH008",
        "Family": "Watches",
        "Color__c": "Black",
        "Size__c": "42mm",
        "Description": "Sophisticated watch with black leather band, black dial with silver accents, Swiss-made movement, date function, water-resistant, 42mm case, ideal for formal or casual attire.",
        "Image_URL__c": "https://n.nordstrommedia.com/it/6a3e849c-453b-4127-b62d-6407305ef625.jpeg?h=368&w=240&dpr=2",
        "Price__c": 109.99
    },
    {
        "Name": "Men's Fitness Tracker Watch - Green",
        "ProductCode": "WATCH009",
        "Family": "Watches",
        "Color__c": "Green",
        "Size__c": "42mm",
        "Description": "Green fitness tracker watch with heart rate monitoring, step counting, sleep tracking, IP68 waterproof rating, touchscreen display, long battery life, compatible with smartphones for notifications.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/71Cn-zLQyFL.jpg",
        "Price__c": 89.99
    },
    {
        "Name": "Men's Luxury Watch - Gold",
        "ProductCode": "WATCH010",
        "Family": "Watches",
        "Color__c": "Gold",
        "Size__c": "45mm",
        "Description": "Opulent gold luxury watch with tourbillon mechanism, carved tiger design on skeleton dial, moon phase display, self-winding automatic movement, leather strap, 45mm case, a statement piece for collectors.",
        "Image_URL__c": "https://m.media-amazon.com/images/I/81dhIIIq+fL._UY1000_.jpg",
        "Price__c": 299.99
    }
]

# --- Upload products + create pricebook entries ---
created = []
for product in products:
    try:
        # ✅ Clean long Google redirect image URLs
        product["Image_URL__c"] = clean_image_url(product["Image_URL__c"])

        # Check if product already exists
        existing = sf.query(f"SELECT Id FROM Product2 WHERE ProductCode = '{product['ProductCode']}' LIMIT 1")

        if existing["records"]:
            product_id = existing["records"][0]["Id"]
            print(f"⚙️ Product already exists, updating: {product['Name']}")
            sf.Product2.update(product_id, product)
        else:
            result = sf.Product2.create(product)
            product_id = result["id"]
            print(f"✅ Created product: {product['Name']} ({product['ProductCode']})")

        # Create or update pricebook entry
        price_entry = sf.query(f"""
            SELECT Id FROM PricebookEntry
            WHERE Pricebook2Id = '{pricebook_id}' AND Product2Id = '{product_id}' LIMIT 1
        """)

        if price_entry["records"]:
            print(f"🔁 PricebookEntry already exists for {product['Name']}")
        else:
            sf.PricebookEntry.create({
                "Pricebook2Id": pricebook_id,
                "Product2Id": product_id,
                "UnitPrice": product["Price__c"],
                "IsActive": True
            })
            print(f"💲 Added PricebookEntry for {product['Name']} at ${product['Price__c']}")

        created.append(product["Name"])

    except Exception as e:
        print(f"⚠️ Error processing {product['Name']}: {e}")

print(f"\n🎉 Successfully added or updated {len(created)} products to Salesforce (with pricebook entries)!")
