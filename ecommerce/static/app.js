var I18N = {
  de: { search: "Suche...", searchBtn: "Suchen", orders: "Bestellungen", cart: "Warenkorb", cartTitle: "Warenkorb", total: "Gesamt:", checkout: "Zur Kasse", empty: "Ihr Warenkorb ist leer", added: "Erfolgreich in den Warenkorb gelegt.", ordered: "Bestellung(en) erfolgreich!", noOrders: "Noch keine Bestellungen", stock: "Auf Lager", out: "Ausverkauft", all: "Alle", qty: "Anzahl", subtotal: "Zwischensumme" },
  en: { search: "Search...", searchBtn: "Search", orders: "Orders", cart: "Cart", cartTitle: "Your Cart", total: "Total:", checkout: "Checkout", empty: "Your cart is empty", added: "Successfully added to cart.", ordered: "Order(s) placed successfully!", noOrders: "No orders yet", stock: "In stock", out: "Out of stock", all: "All", qty: "Qty", subtotal: "Subtotal" },
  zh: { search: "搜索...", searchBtn: "搜索", orders: "我的订单", cart: "购物车", cartTitle: "购物车", total: "合计:", checkout: "去结算", empty: "购物车是空的", added: "已成功加入购物车", ordered: "下单成功!", noOrders: "暂无订单", stock: "有货", out: "缺货", all: "全部", qty: "数量", subtotal: "小计" }
};

function t(key) {
  var lang = localStorage.getItem('lang') || 'de';
  return (I18N[lang] && I18N[lang][key]) || key;
}
function changeLang(lang) { localStorage.setItem('lang', lang); applyLang(); load(); loadCats(); }
function applyLang() {
  var lang = localStorage.getItem('lang') || 'de';
  if (document.getElementById('langSel')) document.getElementById('langSel').value = lang;
  if (document.getElementById('q')) document.getElementById('q').placeholder = t('search');
  if (document.getElementById('searchBtn')) document.getElementById('searchBtn').textContent = t('searchBtn');
  if (document.getElementById('ordersLink')) document.getElementById('ordersLink').textContent = t('orders');
  if (document.getElementById('cartTitle')) document.getElementById('cartTitle').textContent = t('cartTitle');
  if (document.getElementById('totalLabel')) document.getElementById('totalLabel').textContent = t('total');
  if (document.getElementById('checkoutBtn')) document.getElementById('checkoutBtn').textContent = t('checkout');
  var cl = document.getElementById('cartLink');
  if (cl) cl.childNodes[0].textContent = t('cart');
}

var cart = JSON.parse(localStorage.getItem('cart') || '[]');
function saveC() { localStorage.setItem('cart', JSON.stringify(cart)); updB(); }
function updB() { var n = 0; cart.forEach(function(i) { n += i.qty; }); var b = document.getElementById('badge'); if (b) b.textContent = n; }
function toast(msg) {
  var el = document.getElementById('toast');
  if (!el) { el = document.createElement('div'); el.id = 'toast'; el.style.cssText = 'display:none;position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#fff;color:#333;padding:14px 24px;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.15);z-index:999;display:none;align-items:center;gap:10px;font-size:14px'; document.body.appendChild(el); }
  el.innerHTML = '<span style="color:#28a745;font-size:18px">&#10004;</span> ' + msg + ' <span style="cursor:pointer;margin-left:12px;color:#999" onclick="this.parentElement.style.display=\'none\'">&#10005;</span>';
  el.style.display = 'flex';
  setTimeout(function() { el.style.display = 'none'; }, 3000);
}
function toggleCart() { document.getElementById('drawer').classList.toggle('open'); document.getElementById('ov').classList.toggle('open'); renderC(); }
function renderC() {
  var b = document.getElementById('cbody'); if (!b) return;
  if (!cart.length) { b.innerHTML = '<p style="color:#999;text-align:center;padding:40px">' + t('empty') + '</p>'; document.getElementById('total').textContent = 'EUR 0'; return; }
  b.innerHTML = ''; var total = 0;
  cart.forEach(function(it, i) { total += it.price * it.qty; b.innerHTML += '<div class="ci"><div style="flex:1"><div style="font-size:13px">' + it.name + '</div><div class="price">EUR' + it.price.toFixed(2) + '</div></div><div><button onclick="chg(' + i + ',-1)">-</button> ' + it.qty + ' <button onclick="chg(' + i + ',1)">+</button></div></div>'; });
  document.getElementById('total').textContent = 'EUR ' + total.toFixed(2);
}
function chg(i, d) { cart[i].qty += d; if (cart[i].qty <= 0) cart.splice(i, 1); saveC(); renderC(); }
function addC(p) { var f = null; cart.forEach(function(i) { if (i.id == p.id) f = i; }); if (f) f.qty++; else cart.push({id: p.id, name: p.name, price: p.price, qty: 1}); saveC(); renderC(); toast(t('added')); }
async function checkout() {
  if (!cart.length) return;
  for (var i = 0; i < cart.length; i++) { await fetch('/api/orders', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({product_id: cart[i].id})}); }
  var n = cart.length; cart = []; saveC(); renderC(); toggleCart(); toast(n + ' ' + t('ordered')); load();
}

var cat = '', pg = 1, q = '';
async function loadCats() {
  var n = document.getElementById('nav'); if (!n) return;
  var d = await (await fetch('/api/categories')).json();
  n.innerHTML = '<a href="#" onclick="showAll()">' + t('all') + '</a>';
  d.forEach(function(c) { n.innerHTML += '<a href="#" onclick="showCat(\'' + c + '\')">' + c + '</a>'; });
}
function showAll() { cat = ''; q = ''; pg = 1; load(); }
function showCat(c) { cat = c; q = ''; pg = 1; load(); }
function doSearch() { var kw = document.getElementById('q').value; if (location.pathname !== '/') { location.href = '/?q=' + encodeURIComponent(kw); } else { q = kw; pg = 1; load(); } }

function buildPagination(totalPages, current) {
  var html = '';
  html += '<button onclick="pg=' + (current > 1 ? current - 1 : 1) + ';load()" ' + (current <= 1 ? 'disabled' : '') + ' style="padding:8px 12px;border:1px solid #ddd;background:#fff;cursor:pointer;border-radius:4px">&lt;</button>';
  var pages = [];
  if (totalPages <= 7) { for (var i = 1; i <= totalPages; i++) pages.push(i); }
  else { pages.push(1); if (current > 3) pages.push('...'); for (var i = Math.max(2, current - 1); i <= Math.min(totalPages - 1, current + 1); i++) pages.push(i); if (current < totalPages - 2) pages.push('...'); pages.push(totalPages); }
  pages.forEach(function(p) { if (p === '...') { html += '<span style="padding:8px">...</span>'; } else { var active = p == current; html += '<button onclick="pg=' + p + ';load()" style="padding:8px 14px;border:1px solid ' + (active ? '#e2231a' : '#ddd') + ';background:' + (active ? '#e2231a' : '#fff') + ';color:' + (active ? '#fff' : '#333') + ';cursor:pointer;border-radius:4px;margin:0 2px">' + p + '</button>'; } });
  html += '<button onclick="pg=' + (current < totalPages ? current + 1 : totalPages) + ';load()" ' + (current >= totalPages ? 'disabled' : '') + ' style="padding:8px 12px;border:1px solid #ddd;background:#fff;cursor:pointer;border-radius:4px">&gt;</button>';
  return html;
}

async function load() {
  var g = document.getElementById('grid'); if (!g) return;
  var u = '/api/products?page=' + pg + '&per=20';
  if (cat) u += '&category=' + encodeURIComponent(cat);
  if (q) u += '&search=' + encodeURIComponent(q);
  var d = await (await fetch(u)).json();
  g.innerHTML = '';
  d.products.forEach(function(p) {
    var sc = p.stock > 10 ? 'ok' : 'low';
    var stockText = p.stock > 0 ? t('stock') + ' (' + p.stock + ')' : t('out');
    g.innerHTML += '<div class="card" onclick="location.href=\'/product/' + p.id + '\'">' +
      '<img src="' + p.image + '" onerror="this.style.background=\'#eee\'">' +
      '<div class="cb"><div class="pname">' + p.name + '</div>' +
      '<div class="price">EUR' + p.price.toFixed(2) + '</div>' +
      '<div class="' + sc + '">' + stockText + '</div>' +
      '<button class="btn" onclick="event.stopPropagation();addC(' + JSON.stringify(p).replace(/"/g, '&quot;') + ')">' + t('cart') + '</button>' +
      '</div></div>';
  });
  var pa = document.getElementById('pag'); pa.innerHTML = buildPagination(d.total_pages, pg);
}

async function loadOrders() {
  var d = await (await fetch('/api/orders')).json();
  var h = document.getElementById('ob');
  if (!d.length) { h.innerHTML = '<p style="color:#999;text-align:center;padding:40px">' + t('noOrders') + '</p>'; return; }

  var groups = {};
  d.forEach(function(o) {
    var key = o.product_name;
    if (!groups[key]) groups[key] = { name: o.product_name, price: o.price, qty: 0, image: o.image, pid: o.pid, lastDate: o.created_at };
    groups[key].qty++;
  });
  var list = Object.values(groups);

  var html = '<div style="padding:16px 0;font-weight:600;font-size:18px">' + d.length + ' Bestellungen</div>';
  html += '<table style="width:100%;border-collapse:collapse">';
  html += '<tr style="border-bottom:2px solid #eee;background:#fafafa"><th style="padding:12px;text-align:left">Produkt</th><th style="padding:12px;text-align:center">' + t('qty') + '</th><th style="padding:12px;text-align:right">Preis</th><th style="padding:12px;text-align:right">' + t('subtotal') + '</th><th style="padding:12px;text-align:left">Status</th><th style="padding:12px;text-align:left">Datum</th></tr>';
  list.forEach(function(g) {
    var img = g.image ? '<img src="' + g.image + '" style="width:60px;height:60px;object-fit:cover;border-radius:4px;vertical-align:middle;margin-right:12px">' : '';
    var link = g.pid ? '<a href="/product/' + g.pid + '" style="text-decoration:none;color:#333">' + img + g.name.substring(0, 60) + '</a>' : img + g.name.substring(0, 60);
    var sub = (g.price * g.qty).toFixed(2);
    html += '<tr style="border-bottom:1px solid #eee">';
    html += '<td style="padding:16px">' + link + '</td>';
    html += '<td style="padding:16px;text-align:center"><span style="background:#f0f0f0;padding:4px 12px;border-radius:12px;font-weight:600">' + g.qty + '</span></td>';
    html += '<td style="padding:16px;text-align:right;color:#666">EUR' + g.price.toFixed(2) + '</td>';
    html += '<td style="padding:16px;text-align:right;font-weight:700;font-size:16px">EUR' + sub + '</td>';
    html += '<td style="padding:16px"><span style="background:#d4edda;color:#155724;padding:4px 10px;border-radius:4px;font-size:12px">confirmed</span></td>';
    html += '<td style="padding:16px;color:#999;font-size:13px">' + g.lastDate.substring(0, 16) + '</td>';
    html += '</tr>';
  });
  html += '</table>';
  h.innerHTML = html;
}

function initIndex() {
  var params = new URLSearchParams(location.search);
  if (params.get('q')) { document.getElementById('q').value = params.get('q'); q = params.get('q'); }
  applyLang(); loadCats(); load(); updB();
}

window.addEventListener('DOMContentLoaded', function() {
  applyLang();
  if (document.getElementById('grid')) initIndex();
  if (document.getElementById('ob')) loadOrders();
});
