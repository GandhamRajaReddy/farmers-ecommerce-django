// static/js/navbar.js
// Handles navbar interactions + cart badge update for AgriMart

// (function () {

//     const mobileToggle = document.querySelector('.navbar-toggle');
//     const mobileMenu = document.querySelector('.navbar-menu');
//     const cartCountEls = document.querySelectorAll('#cart-count, .cart-count');

//     // Toggle mobile menu
//     if (mobileToggle && mobileMenu) {
//         mobileToggle.addEventListener('click', () => {
//             mobileMenu.classList.toggle('open');
//             mobileToggle.classList.toggle('open');
//         });
//     }

//     // Close menu when clicking on any link
//     document.addEventListener('click', function (e) {
//         const link = e.target.closest('.navbar-menu a');
//         if (link && mobileMenu?.classList.contains('open')) {
//             mobileMenu.classList.remove('open');
//             mobileToggle.classList.remove('open');
//         }
//     });

//     // Helper — get total items in cart
//     function getCartCount() {
//         try {
//             const cart = JSON.parse(localStorage.getItem('cart')) || [];
//             return cart.reduce((sum, item) => sum + (item.qty || 0), 0);
//         } catch {
//             return 0;
//         }
//     }

//     // Update visible cart count
//     function updateCartCount(count) {
//         cartCountEls.forEach(el => {
//             el.textContent = count;
//             el.style.display = count > 0 ? 'inline-block' : 'none';
//         });
//     }

//     // Initialize with current count
//     updateCartCount(getCartCount());

//     // When cart.js dispatches updates
//     window.addEventListener('cart-updated', () => {
//         updateCartCount(getCartCount());
//     });

// })();
// document.getElementById("nav-toggle").onclick = function () {
//     document.getElementById("nav-center").classList.toggle("open");
// };
document.addEventListener("DOMContentLoaded", function () {
    const hamburger = document.querySelector(".hamburger");
    const navMenu = document.getElementById("nav-center");

    if (!hamburger || !navMenu) return;

    hamburger.addEventListener("click", function () {
        const isExpanded = hamburger.getAttribute("aria-expanded") === "true";

        // Toggle aria-expanded
        hamburger.setAttribute("aria-expanded", String(!isExpanded));

        // Toggle menu visibility
        navMenu.classList.toggle("open");
    });
});
