from playwright.sync_api import sync_playwright
import psycopg2, time, re

DB = {'host': '192.168.0.155', 'database': 'shop', 'user': 'shop', 'password': 'shop123'}

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]
    page = context.new_page()

    print("Opening joybuy.de ...")
    page.goto("https://www.joybuy.de/", wait_until="networkidle", timeout=30000)
    time.sleep(5)

    # Auto-discover all categories
    all_links = page.query_selector_all("a")
    cats = []
    seen = set()
    for a in all_links:
        href = a.get_attribute("href") or ""
        text = a.inner_text().strip()
        if text and "/minihome/" in href and text not in seen:
            seen.add(text)
            url = "https://www.joybuy.de" + href if href.startswith("/") else href
            cats.append((text, url))
            print(f"  Category: {text}")

    print(f"\nFound {len(cats)} categories, scraping products...\n")

    all_products = []
    for cat_name, cat_url in cats:
        print(f"--- {cat_name} ---")
        try:
            page.goto(cat_url, wait_until="networkidle", timeout=30000)
            time.sleep(4)
            cards = page.query_selector_all("a[href*='/dp/']")
            seen_p = set()
            for a in cards:
                card = a
                for _ in range(5):
                    card = card.query_selector("xpath=..")
                    if not card: break
                try:
                    txt = card.inner_text()
                    img_el = card.query_selector("img")
                    img_url = img_el.get_attribute("src") if img_el else ""
                    lines = [l.strip() for l in txt.split("\n") if l.strip()]
                    price = None
                    name = None
                    for l in lines:
                        m = re.search(r"(\d+[.,]\d{2})", l)
                        if m and not price:
                            price = float(m.group(1).replace(",", "."))
                    for l in lines:
                        if len(l) > 10 and "Sofort" not in l and "Lieferung" not in l:
                            name = l; break
                    if name and price and name not in seen_p:
                        seen_p.add(name)
                        all_products.append({"name": name, "category": cat_name, "price": price, "image": img_url, "stock": 50})
                        print(f"  {name[:40]} - EUR{price}")
                except: pass
        except Exception as e:
            print(f"  Failed: {e}")

    page.close()

print(f"\nTotal: {len(all_products)} products")
conn = psycopg2.connect(**DB)
cur = conn.cursor()
cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS image TEXT;")
cur.execute("DELETE FROM products;")
for prod in all_products:
    cur.execute("INSERT INTO products (name,category,price,description,stock,image) VALUES (%s,%s,%s,%s,%s,%s)",
                (prod["name"][:200], prod["category"], prod["price"], "", prod["stock"], prod["image"]))
conn.commit()
print(f"Inserted {len(all_products)} rows")
cur.execute("SELECT category, count(*) FROM products GROUP BY category ORDER BY count(*) DESC;")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")
conn.close()
