// static/js/cart.js
// Server-backed cart integration for AgriMart (Django endpoints)

(function () {
  // CSRF token helper (works whether token is in window or in a form)
  const csrfToken =
    window.csrfToken ||
    document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
    null;

  function jsonFetch(url, method = "GET", data = null) {
    const opts = { method, headers: {} };
    if (csrfToken) opts.headers["X-CSRFToken"] = csrfToken;
    if (method !== "GET" && data !== null) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(data);
    }
    return fetch(url, opts).then((r) => r.json());
  }

  // -------------------------
  // Notifications
  // -------------------------
  function notify(msg, opts = {}) {
    const el = document.createElement("div");
    el.className = "agrimart-notification";
    el.style = `
      position: fixed;
      top: 80px;
      right: 20px;
      background: ${opts.bg || "#2e7d32"};
      color: white;
      padding: 10px 14px;
      border-radius: 6px;
      z-index: 1200;
      box-shadow: 0 6px 18px rgba(0,0,0,0.12);
      font-weight:600;
    `;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => {
      el.style.transition = "opacity 0.25s, transform 0.25s";
      el.style.opacity = "0";
      el.style.transform = "translateY(-8px)";
      setTimeout(() => el.remove(), 300);
    }, opts.duration || 2000);
  }

  // -------------------------
  // Update cart count UI
  // -------------------------
  function updateCartCountUI(count) {
    const els = document.querySelectorAll("#cart-count, .cart-count");
    els.forEach((el) => {
      el.textContent = count;
      el.style.display = count > 0 ? "inline-block" : "none";
    });
  }

  // Fetch and refresh cart count from server
  function refreshCartCount() {
    jsonFetch("/cart/count/")
      .then((resp) => {
        if (resp && typeof resp.cart_count !== "undefined") {
          updateCartCountUI(resp.cart_count);
        }
      })
      .catch((e) => {
        // silent fail
        // console.warn("cart count fetch failed", e);
      });
  }

  // -------------------------
  // Add to cart (called by click delegation or externally)
  // -------------------------
  async function addToCartHandler(productId, quantity = 1, options = {}) {
    try {
      const resp = await jsonFetch("/cart/add/", "POST", {
        product_id: productId,
        quantity: quantity,
      });

      if (!resp || !resp.success) {
        notify(resp?.error || "Could not add to cart", { bg: "#d32f2f" });
        return resp;
      }

      // Update UI: cart count, subtotal if available
      if (typeof resp.cart_count !== "undefined") updateCartCountUI(resp.cart_count);
      if (typeof resp.cart_total !== "undefined") {
        const totalEls = document.querySelectorAll("#cart-total, .cart-total");
        totalEls.forEach((el) => (el.textContent = `₹${resp.cart_total}`));
      }

      // Dispatch app-wide event NAVBAR listens to
      window.dispatchEvent(new Event("cart-updated"));
      notify(resp.message || "Added to cart");

      // If caller requested redirect (buy now)
      if (options.redirect) {
        window.location.href = "/checkout/";
      }

      return resp;
    } catch (err) {
      notify("Server error adding to cart", { bg: "#d32f2f" });
      return { success: false, error: String(err) };
    }
  }

  // Expose global function used by main.js (keeps backward-compatible)
  window.addToCart = function (productId, qty = 1, redirectToCheckout = false) {
    return addToCartHandler(productId, qty, { redirect: !!redirectToCheckout });
  };

  // -------------------------
  // Update cart item quantity
  // -------------------------
  async function updateCartItem(itemId, quantity) {
    try {
      const resp = await jsonFetch("/cart/update/", "POST", {
        item_id: itemId,
        quantity: quantity,
      });

      if (!resp || !resp.success) {
        notify(resp?.error || "Could not update item", { bg: "#d32f2f" });
        return resp;
      }

      // Update subtotal and item total in the DOM if present
      if (typeof resp.subtotal !== "undefined") {
        const subtotalEls = document.querySelectorAll("#cart-total, .cart-total");
        subtotalEls.forEach((el) => (el.textContent = `₹${resp.subtotal}`));
      }

      if (typeof resp.cart_count !== "undefined") updateCartCountUI(resp.cart_count);

      window.dispatchEvent(new Event("cart-updated"));
      return resp;
    } catch (err) {
      notify("Server error updating cart", { bg: "#d32f2f" });
      return { success: false, error: String(err) };
    }
  }

  // Expose utility:
  window.cartUpdateItem = window.cartUpdateItem || function (itemId, qty) {
    return updateCartItem(itemId, qty);
  };

  // -------------------------
  // Remove cart item
  // -------------------------
  async function removeCartItem(itemId) {
    try {
      const resp = await jsonFetch("/cart/remove/", "POST", {
        item_id: itemId,
      });

      if (!resp || !resp.success) {
        notify(resp?.error || "Could not remove item", { bg: "#d32f2f" });
        return resp;
      }

      // Update cart count and subtotal
      if (typeof resp.cart_count !== "undefined") updateCartCountUI(resp.cart_count);
      if (typeof resp.subtotal !== "undefined") {
        const subtotalEls = document.querySelectorAll("#cart-total, .cart-total");
        subtotalEls.forEach((el) => (el.textContent = `₹${resp.subtotal}`));
      }

      // Remove item row if present
      const row = document.querySelector(`[data-item-id="${itemId}"]`);
      if (row) row.remove();

      window.dispatchEvent(new Event("cart-updated"));
      notify(resp.message || "Item removed");
      return resp;
    } catch (err) {
      notify("Server error removing item", { bg: "#d32f2f" });
      return { success: false, error: String(err) };
    }
  }

  window.cartRemoveItem = window.cartRemoveItem || function (itemId) {
    return removeCartItem(itemId);
  };

  // -------------------------
  // Clear cart
  // -------------------------
  async function clearCart() {
    try {
      const resp = await jsonFetch("/cart/clear/", "POST", {});
      if (resp && resp.success) {
        updateCartCountUI(0);
        const cartItems = document.getElementById("cart-items");
        const cartWrapper = document.getElementById("cart-wrapper");
        const cartEmpty = document.getElementById("cart-empty");
        if (cartItems) cartItems.innerHTML = "";
        if (cartWrapper) cartWrapper.style.display = "none";
        if (cartEmpty) cartEmpty.style.display = "block";
        window.dispatchEvent(new Event("cart-updated"));
        notify("Cart cleared");
      } else {
        notify(resp?.error || "Could not clear cart", { bg: "#d32f2f" });
      }
      return resp;
    } catch (err) {
      notify("Server error clearing cart", { bg: "#d32f2f" });
      return { success: false, error: String(err) };
    }
  }

  window.clearCartServer = clearCart;

  // -------------------------
  // Click delegation for add-to-cart, qty toggles, remove
  // -------------------------
  function setupDelegation() {
    document.addEventListener("click", (e) => {
      // Add to cart buttons (product lists + quick view + product detail)
      const addBtn = e.target.closest(".add-to-cart, .add-btn, .btn-add-to-cart");
      if (addBtn) {
        e.preventDefault();
        // read product id and quantity
        const productId =
          addBtn.dataset.productId ||
          addBtn.closest(".product-card")?.dataset.id ||
          addBtn.closest("[data-id]")?.dataset.id;
        let qty = parseInt(addBtn.dataset.quantity || 1, 10);
        // if no qty on button, try nearest quantity input
        if (!qty || qty < 1) {
          const qtyInput =
            addBtn.closest(".product-detail-page")?.querySelector("#quantity") ||
            document.querySelector("#quantity");
          if (qtyInput) qty = parseInt(qtyInput.value || 1, 10);
          else qty = 1;
        }
        if (!productId) {
          notify("Product ID not found", { bg: "#d32f2f" });
          return;
        }
        addToCartHandler(productId, qty, { redirect: !!addBtn.dataset.redirect });
        return;
      }

      // Cart increase/decrease controls (data attributes)
      const qtyBtn = e.target.closest("[data-cart-action]");
      if (qtyBtn) {
        const action = qtyBtn.dataset.cartAction;
        const itemId = qtyBtn.dataset.itemId;
        const currentQty = parseInt(qtyBtn.dataset.currentQty || qtyBtn.closest("[data-quantity]")?.dataset.quantity || 0, 10);

        if (!itemId) return;
        if (action === "increase") {
          window.cartUpdateItem(itemId, currentQty + 1);
        } else if (action === "decrease") {
          window.cartUpdateItem(itemId, Math.max(0, currentQty - 1));
        }
        return;
      }

      // Remove buttons that use class .cart-remove or data-remove-id
      const rem = e.target.closest(".cart-remove, [data-remove-id]");
      if (rem) {
        e.preventDefault();
        const itemId = rem.dataset.removeId || rem.dataset.itemId || rem.closest("[data-item-id]")?.dataset.itemId;
        if (!itemId) return;
        removeCartItem(itemId);
        return;
      }
    });
  }

  // -------------------------
  // Initialize on DOM ready
  // -------------------------
  document.addEventListener("DOMContentLoaded", () => {
    refreshCartCount();
    setupDelegation();

    // If on cart page server-rendered, attach inline quantity input listeners
    const cartItemsTable = document.getElementById("cart-items");
    if (cartItemsTable) {
      // Handle numeric input changes (if present)
      cartItemsTable.addEventListener("change", (e) => {
        const input = e.target.closest("input[data-item-id]");
        if (input) {
          const itemId = input.dataset.itemId;
          const qty = parseInt(input.value || 0, 10);
          window.cartUpdateItem(itemId, qty);
        }
      });

      // If cart rows are rendered server-side with buttons using onclick="cartUpdateItem(...)" those will still work
    }
  });

  // expose some methods for templates that call them directly (backwards compatibility)
  window.refreshCartCount = refreshCartCount;
  window.serverCart = {
    add: addToCartHandler,
    update: updateCartItem,
    remove: removeCartItem,
    clear: clearCart,
  };
})();
document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-to-cart")) {

        const productId = e.target.dataset.productId;

        fetch("/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.csrfToken
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: 1
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll("#cart-count")
                    .forEach(el => el.innerText = data.cart_count);
            } else {
                alert(data.error);
            }
        });
    }
});

