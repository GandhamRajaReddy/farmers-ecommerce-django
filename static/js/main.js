// static/js/main.js
// AgriMart — Core Frontend Logic

// -------------------------------
// CSRF TOKEN HANDLING
// -------------------------------
const csrfToken =
    window.csrfToken ||
    document.querySelector("input[name=csrfmiddlewaretoken]")?.value ||
    null;

function ajax(url, method = "GET", data = null) {
    const options = { method, headers: {} };

    if (csrfToken) {
        options.headers["X-CSRFToken"] = csrfToken;
    }

    if (method !== "GET" && data !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    return fetch(url, options).then((res) => res.json());
}

// -------------------------------
// ADD TO CART + BUY NOW
// -------------------------------
window.addToCart = function (productId, qty = 1, redirectToCheckout = false) {
    ajax("/cart/add/", "POST", { product_id: productId, quantity: qty })
        .then((data) => {
            if (!data.success) {
                alert(data.error || "Unable to add to cart.");
                return;
            }

            // Trigger navbar update
            window.dispatchEvent(new Event("cart-updated"));

            if (redirectToCheckout) {
                window.location.href = "/checkout/";
            } else {
                alert("Product added to cart!");
            }
        })
        .catch(() => alert("Cart error — please try again."));
};

// -------------------------------
// QUICK VIEW HANDLER
// -------------------------------
document.addEventListener("click", function (event) {
    const btn = event.target.closest(".btn-quick-view, .quick-view");
    if (!btn) return;

    const productId = btn.dataset.productId;
    if (!productId) return;

    // CORRECT DJANGO URL
    fetch(`/product/${productId}/quick-view/`)
        .then((res) => res.json())
        .then((data) => {
            if (!data.html) {
                alert("Unable to load product preview.");
                return;
            }

            // Create modal if needed
            let modal = document.getElementById("quickViewModal");
            if (!modal) {
                modal = document.createElement("div");
                modal.id = "quickViewModal";
                modal.className = "modal";
                modal.innerHTML = `
                    <div class="modal-content">
                        <span class="close">&times;</span>
                        <div id="quickViewContent"></div>
                    </div>
                `;
                document.body.appendChild(modal);
            }

            document.getElementById("quickViewContent").innerHTML = data.html;
            modal.style.display = "block";

            modal.querySelector(".close").onclick = () => {
                modal.style.display = "none";
            };
        })
        .catch(() => alert("Quick view failed — please try again."));
});

// Close modal on outside click
window.addEventListener("click", function (event) {
    const modal = document.getElementById("quickViewModal");
    if (modal && event.target === modal) {
        modal.style.display = "none";
    }
});

// -------------------------------
// WISHLIST
// -------------------------------
document.addEventListener("click", function (e) {
    const btn = e.target.closest(".btn-wishlist, .wishlist-toggle");
    if (!btn) return;

    const productId = btn.dataset.productId;
    if (!productId) return;

    ajax("/wishlist/add/", "POST", { product_id: productId })
        .then((data) => {
            if (data.success) {
                btn.classList.add("in-wishlist");
                alert("Added to wishlist!");
            } else {
                alert(data.error || "Wishlist error.");
            }
        })
        .catch(() => alert("Wishlist request failed."));
});

// -------------------------------
// FUTURE INITIALIZERS
// -------------------------------
document.addEventListener("DOMContentLoaded", function () {
    // placeholder for future improvements
});
