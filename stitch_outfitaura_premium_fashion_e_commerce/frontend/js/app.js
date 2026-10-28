/**
 * OutfitAura Shared Luxury E-Commerce Engine
 */

const API_BASE = '/api';

// Generate or retrieve persistent guest session ID
function getSessionId() {
    let sid = localStorage.getItem('outfitaura_session_id');
    if (!sid) {
        sid = 'guest_' + Math.random().toString(36).substring(2, 11);
        localStorage.setItem('outfitaura_session_id', sid);
    }
    return sid;
}

// Global API Helper
async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'X-Session-ID': getSessionId(),
        ...(options.headers || {})
    };
    
    const token = localStorage.getItem('outfitaura_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'An error occurred');
    }
    return data;
}

// Toast notification helper
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-6 right-6 z-50 flex flex-col gap-2 max-w-sm pointer-events-none';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `px-5 py-3 rounded-lg shadow-xl backdrop-blur-md font-body-md text-sm transition-all duration-300 transform translate-y-2 opacity-0 pointer-events-auto flex items-center justify-between gap-3 ${
        type === 'error' 
            ? 'bg-red-900/90 text-white border border-red-700' 
            : 'bg-stone-900/90 text-stone-100 border border-stone-700'
    }`;
    toast.innerHTML = `
        <span>${message}</span>
        <button class="opacity-70 hover:opacity-100">&times;</button>
    `;

    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    });

    toast.querySelector('button').addEventListener('click', () => {
        toast.remove();
    });

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Cart Drawer Component Logic
class CartDrawer {
    constructor() {
        this.isOpen = false;
        this.cart = { items: [], subtotal: 0, total: 0, total_items: 0 };
        this.init();
    }

    init() {
        this.renderDrawer();
        this.bindEvents();
        this.refreshCart();
    }

    renderDrawer() {
        if (document.getElementById('cart-drawer')) return;

        const drawerHTML = `
        <div id="cart-drawer-overlay" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 opacity-0 pointer-events-none transition-opacity duration-300"></div>
        <div id="cart-drawer" class="fixed top-0 right-0 h-full w-full max-w-md bg-stone-50 dark:bg-stone-900 shadow-2xl z-50 transform translate-x-full transition-transform duration-300 flex flex-col border-l border-stone-200 dark:border-stone-800">
            <!-- Header -->
            <div class="p-6 border-b border-stone-200 dark:border-stone-800 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <h3 class="font-serif text-2xl font-medium tracking-tight text-stone-900 dark:text-stone-100">Shopping Bag</h3>
                    <span id="cart-drawer-count" class="text-xs bg-stone-200 dark:bg-stone-800 text-stone-700 dark:text-stone-300 px-2 py-0.5 rounded-full font-bold">0</span>
                </div>
                <button id="cart-close-btn" class="p-2 text-stone-500 hover:text-stone-900 dark:hover:text-stone-100 transition-colors">
                    <span class="material-symbols-outlined text-2xl">close</span>
                </button>
            </div>

            <!-- Items list -->
            <div id="cart-items-container" class="flex-1 overflow-y-auto p-6 space-y-4 divide-y divide-stone-100 dark:divide-stone-800">
                <div class="text-center py-12 text-stone-400">
                    <span class="material-symbols-outlined text-5xl mb-2 stroke-1">shopping_bag</span>
                    <p class="font-sans">Your shopping bag is empty.</p>
                    <a href="/shop.html" class="inline-block mt-4 text-xs font-bold uppercase tracking-widest text-stone-900 dark:text-stone-100 border-b border-stone-900 pb-1">Discover the Collection</a>
                </div>
            </div>

            <!-- Footer / Checkout -->
            <div class="p-6 border-t border-stone-200 dark:border-stone-800 bg-stone-100/50 dark:bg-stone-900/50 space-y-3">
                <div class="flex justify-between text-sm text-stone-600 dark:text-stone-400">
                    <span>Subtotal</span>
                    <span id="cart-subtotal" class="font-medium text-stone-900 dark:text-stone-100">$0.00</span>
                </div>
                <div class="flex justify-between text-sm text-stone-600 dark:text-stone-400">
                    <span>Complimentary Shipping</span>
                    <span class="text-xs text-emerald-600 dark:text-emerald-400 uppercase font-bold tracking-wider">Eligible</span>
                </div>
                <div class="flex justify-between text-base font-semibold text-stone-900 dark:text-stone-100 pt-2 border-t border-stone-200 dark:border-stone-800">
                    <span>Estimated Total</span>
                    <span id="cart-total">$0.00</span>
                </div>
                <button id="checkout-btn" class="w-full bg-stone-900 text-stone-50 dark:bg-stone-100 dark:text-stone-900 py-3.5 rounded-lg uppercase tracking-widest text-xs font-bold hover:bg-stone-800 dark:hover:bg-white transition-all shadow-md mt-2">
                    Proceed to Checkout
                </button>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', drawerHTML);
    }

    bindEvents() {
        document.querySelectorAll('[data-open-cart]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.open();
            });
        });

        document.getElementById('cart-close-btn')?.addEventListener('click', () => this.close());
        document.getElementById('cart-drawer-overlay')?.addEventListener('click', () => this.close());

        document.getElementById('checkout-btn')?.addEventListener('click', () => {
            if (this.cart.items.length === 0) {
                showToast('Your bag is empty', 'error');
                return;
            }
            this.openCheckoutModal();
        });
    }

    open() {
        this.isOpen = true;
        document.getElementById('cart-drawer-overlay')?.classList.remove('opacity-0', 'pointer-events-none');
        document.getElementById('cart-drawer')?.classList.remove('translate-x-full');
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.isOpen = false;
        document.getElementById('cart-drawer-overlay')?.classList.add('opacity-0', 'pointer-events-none');
        document.getElementById('cart-drawer')?.classList.add('translate-x-full');
        document.body.style.overflow = '';
    }

    async refreshCart() {
        try {
            this.cart = await apiFetch('/cart');
            this.updateBadge();
            this.renderItems();
        } catch (e) {
            console.error('Failed to load cart:', e);
        }
    }

    updateBadge() {
        const count = this.cart.total_items || 0;
        document.querySelectorAll('.cart-badge').forEach(el => {
            el.textContent = count;
            el.style.display = count > 0 ? 'flex' : 'none';
        });
        const drawerCount = document.getElementById('cart-drawer-count');
        if (drawerCount) drawerCount.textContent = count;
    }

    renderItems() {
        const container = document.getElementById('cart-items-container');
        if (!container) return;

        if (!this.cart.items || this.cart.items.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 text-stone-400">
                    <span class="material-symbols-outlined text-5xl mb-2 stroke-1">shopping_bag</span>
                    <p class="font-sans">Your shopping bag is empty.</p>
                    <a href="/shop.html" class="inline-block mt-4 text-xs font-bold uppercase tracking-widest text-stone-900 dark:text-stone-100 border-b border-stone-900 pb-1">Discover the Collection</a>
                </div>
            `;
            document.getElementById('cart-subtotal').textContent = '$0.00';
            document.getElementById('cart-total').textContent = '$0.00';
            return;
        }

        container.innerHTML = this.cart.items.map(item => `
            <div class="flex gap-4 pt-4 first:pt-0">
                <img src="${item.product?.thumbnail || item.product?.images?.[0] || 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=200'}" 
                     alt="${item.product?.name || 'Garment'}" 
                     class="w-20 h-24 object-cover rounded bg-stone-100 dark:bg-stone-800 shrink-0">
                <div class="flex-1 flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-start">
                            <h4 class="font-serif text-sm font-medium text-stone-900 dark:text-stone-100">${item.product?.name || 'Product'}</h4>
                            <button onclick="cartDrawer.removeItem('${item.id}')" class="text-stone-400 hover:text-stone-900 dark:hover:text-stone-100 text-xs">
                                <span class="material-symbols-outlined text-base">delete</span>
                            </button>
                        </div>
                        <p class="text-xs text-stone-500 mt-0.5">${item.color} / Size ${item.size}</p>
                    </div>
                    <div class="flex justify-between items-center mt-2">
                        <div class="flex items-center border border-stone-200 dark:border-stone-700 rounded">
                            <button onclick="cartDrawer.updateQuantity('${item.id}', ${item.quantity - 1})" class="px-2 py-0.5 text-stone-600 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800 text-xs">-</button>
                            <span class="px-2.5 py-0.5 text-xs font-semibold text-stone-900 dark:text-stone-100">${item.quantity}</span>
                            <button onclick="cartDrawer.updateQuantity('${item.id}', ${item.quantity + 1})" class="px-2 py-0.5 text-stone-600 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800 text-xs">+</button>
                        </div>
                        <span class="text-sm font-semibold text-stone-900 dark:text-stone-100">$${item.total_price.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        `).join('');

        document.getElementById('cart-subtotal').textContent = `$${this.cart.subtotal.toFixed(2)}`;
        document.getElementById('cart-total').textContent = `$${this.cart.total.toFixed(2)}`;
    }

    async addItem(productId, size = 'S', color = 'Blush Pink', quantity = 1) {
        try {
            await apiFetch('/cart/items', {
                method: 'POST',
                body: JSON.stringify({ product_id: productId, size, color, quantity })
            });
            await this.refreshCart();
            this.open();
            showToast('Garment added to your bag');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async updateQuantity(itemId, qty) {
        try {
            await apiFetch(`/cart/items/${itemId}`, {
                method: 'PUT',
                body: JSON.stringify({ quantity: qty })
            });
            await this.refreshCart();
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    async removeItem(itemId) {
        try {
            await apiFetch(`/cart/items/${itemId}`, {
                method: 'DELETE'
            });
            await this.refreshCart();
            showToast('Garment removed from bag');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    openCheckoutModal() {
        this.close();
        let modal = document.getElementById('checkout-modal');
        if (!modal) {
            const modalHTML = `
            <div id="checkout-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                <div class="bg-stone-50 dark:bg-stone-900 rounded-xl max-w-lg w-full p-8 shadow-2xl border border-stone-200 dark:border-stone-800 relative max-h-[90vh] overflow-y-auto">
                    <button onclick="document.getElementById('checkout-modal').remove()" class="absolute top-6 right-6 text-stone-400 hover:text-stone-900 dark:hover:text-stone-100">
                        <span class="material-symbols-outlined">close</span>
                    </button>
                    <h3 class="font-serif text-2xl font-bold text-stone-900 dark:text-stone-100 mb-1">Curated Checkout</h3>
                    <p class="font-sans text-xs text-stone-500 uppercase tracking-widest mb-6">OutfitAura Private Concierge</p>

                    <form id="checkout-form" class="space-y-4">
                        <div>
                            <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">Full Name</label>
                            <input type="text" id="chk-name" required value="Aura Muse" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">Phone</label>
                                <input type="tel" id="chk-phone" required value="+91 98765 43210" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">City</label>
                                <input type="text" id="chk-city" required value="Mumbai" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">Street Address</label>
                            <input type="text" id="chk-street" required value="402 Haute Tower, Altamount Road" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                        </div>
                        <div class="grid grid-cols-2 gap-3">
                            <div>
                                <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">State</label>
                                <input type="text" id="chk-state" required value="Maharashtra" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                            </div>
                            <div>
                                <label class="block text-xs uppercase font-bold tracking-wider text-stone-600 dark:text-stone-400 mb-1">PIN / Postal Code</label>
                                <input type="text" id="chk-postal" required value="400026" class="w-full px-3.5 py-2.5 rounded bg-stone-100 dark:bg-stone-800 border-stone-300 dark:border-stone-700 text-sm focus:ring-1 focus:ring-stone-900 focus:outline-none">
                            </div>
                        </div>
                        
                        <div class="pt-4 border-t border-stone-200 dark:border-stone-800">
                            <div class="flex justify-between font-semibold text-sm mb-4">
                                <span>Total to Pay:</span>
                                <span class="font-bold text-base" id="modal-chk-total">$${this.cart.total.toFixed(2)}</span>
                            </div>
                            <button type="submit" class="w-full bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 py-3.5 rounded-lg uppercase tracking-widest text-xs font-bold hover:bg-stone-800 dark:hover:bg-white transition-all shadow-md">
                                Confirm & Complete Order
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('checkout-modal');
        }

        modal.querySelector('#checkout-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const orderItems = this.cart.items.map(it => ({
                product_id: it.product_id,
                product_name: it.product?.name || 'Garment',
                product_image: it.product?.thumbnail || '',
                size: it.size,
                color: it.color,
                price: it.unit_price,
                quantity: it.quantity,
                subtotal: it.total_price
            }));

            const payload = {
                items: orderItems,
                shipping_address: {
                    full_name: document.getElementById('chk-name').value,
                    phone: document.getElementById('chk-phone').value,
                    street: document.getElementById('chk-street').value,
                    city: document.getElementById('chk-city').value,
                    state: document.getElementById('chk-state').value,
                    postal_code: document.getElementById('chk-postal').value,
                    country: "India"
                },
                payment_method: "card"
            };

            try {
                const order = await apiFetch('/orders', {
                    method: 'POST',
                    body: JSON.stringify(payload)
                });
                modal.remove();
                await this.refreshCart();
                this.showOrderSuccess(order);
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    }

    showOrderSuccess(order) {
        const successHTML = `
        <div id="order-success-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
            <div class="bg-stone-50 dark:bg-stone-900 rounded-xl max-w-md w-full p-8 text-center shadow-2xl border border-stone-200 dark:border-stone-800">
                <div class="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span class="material-symbols-outlined text-3xl">check</span>
                </div>
                <h3 class="font-serif text-2xl font-bold text-stone-900 dark:text-stone-100 mb-2">Order Confirmed</h3>
                <p class="font-sans text-xs uppercase tracking-widest text-stone-500 mb-4">Order ${order.order_number}</p>
                <p class="text-sm text-stone-600 dark:text-stone-400 mb-6">Thank you for ordering with OutfitAura. Your pieces are being curated with meticulous care.</p>
                <div class="bg-stone-100 dark:bg-stone-800 p-4 rounded-lg text-left text-xs space-y-1 mb-6">
                    <div class="flex justify-between"><span class="text-stone-500">Total:</span> <span class="font-bold text-stone-900 dark:text-stone-100">$${order.total.toFixed(2)}</span></div>
                    <div class="flex justify-between"><span class="text-stone-500">Status:</span> <span class="text-emerald-600 font-semibold uppercase">${order.order_status}</span></div>
                    <div class="flex justify-between"><span class="text-stone-500">Shipping to:</span> <span class="text-stone-700 dark:text-stone-300">${order.shipping_address.city}, ${order.shipping_address.country}</span></div>
                </div>
                <button onclick="document.getElementById('order-success-modal').remove()" class="w-full bg-stone-900 text-white dark:bg-stone-100 dark:text-stone-900 py-3 rounded uppercase tracking-widest text-xs font-bold hover:bg-stone-800">
                    Continue Exploring
                </button>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', successHTML);
    }
}

// Global Cart Instance
let cartDrawer;
document.addEventListener('DOMContentLoaded', () => {
    cartDrawer = new CartDrawer();
    
    // Bind newsletter forms
    document.querySelectorAll('form[data-newsletter]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const input = form.querySelector('input[type="email"]');
            if (!input || !input.value) return;
            try {
                const res = await apiFetch('/newsletter/subscribe', {
                    method: 'POST',
                    body: JSON.stringify({ email: input.value })
                });
                showToast(res.message || 'Subscribed successfully!');
                input.value = '';
            } catch (err) {
                showToast(err.message, 'error');
            }
        });
    });
});
