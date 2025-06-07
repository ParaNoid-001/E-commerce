// navbar.js

// This function updates the cart count badge
function updateCartCount(count) {
    const badge = document.getElementById('cart-count-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// This function updates the wishlist count badge
function updateWishlistCount(count) {
    const badge = document.getElementById('navbar-wishlist-count');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Initialize cart count on page load
function initializeCounts() {
    // These values will be passed from the template
    if (typeof cartCount !== 'undefined') {
        updateCartCount(cartCount);
    }
    if (typeof wishlistCount !== 'undefined') {
        updateWishlistCount(wishlistCount);
    }
}

document.addEventListener('DOMContentLoaded', initializeCounts);

// Function to get CSRF token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Example AJAX call for adding to cart
function addToCart(productId) {
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `product_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_total);
            // Show success toast/notification
        }
    })
    .catch(error => console.error('Error:', error));
}

// navbar.js
document.addEventListener('DOMContentLoaded', function() {
    // Main container where content will be loaded
    const mainContent = document.querySelector('main.container') || document.getElementById('main-content');
    
    // AI Assistant link handler
    const aiAssistantLink = document.querySelector('a[href*="askquery"]');
    
    if (aiAssistantLink && mainContent) {
        aiAssistantLink.addEventListener('click', function(e) {
            // Only handle if it's the AI Assistant link
            if (this.href.includes('askquery')) {
                e.preventDefault();
                loadAIAssistantContent(this.href);
                
                // Update active state in navbar
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active', 'bg-primary-soft');
                });
                this.classList.add('active', 'bg-primary-soft');
                
                // Update browser history
                history.pushState(null, null, this.href);
            }
        });
    }
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', function() {
        if (location.pathname.includes('askquery')) {
            loadAIAssistantContent(location.href);
        }
    });
    
    // Function to load AI Assistant content via AJAX
    function loadAIAssistantContent(url) {
        // Show loading state
        const originalContent = mainContent.innerHTML;
        mainContent.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-muted">Loading AI Assistant...</p>
            </div>
        `;
        
        // Fetch the content
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.text();
        })
        .then(html => {
            // Update the content
            mainContent.innerHTML = html;
            
            // Initialize any scripts in the loaded content
            initAIAssistantScripts();
            
            // Smooth scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error loading AI Assistant:', error);
            mainContent.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error loading content:</strong> ${error.message}
                    <button class="btn btn-sm btn-outline-secondary ms-3" onclick="window.location.reload()">
                        Reload Page
                    </button>
                </div>
                ${originalContent}
            `;
        });
    }
    
    // Initialize AI Assistant specific scripts
    function initAIAssistantScripts() {
        const chatForm = document.getElementById('chatForm');
        if (chatForm) {
            chatForm.addEventListener('submit', handleChatSubmit);
        }
        
        // Reinitialize any other plugins/components needed
        if (typeof hljs !== 'undefined') {
            document.querySelectorAll('pre code').forEach(block => {
                hljs.highlightElement(block);
            });
        }
    }
    
    // Chat form submission handler
    function handleChatSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const responseContainer = document.getElementById('response');
        const submitBtn = form.querySelector('button[type="submit"]');
        const loadingIndicator = document.getElementById('loading-indicator');
        
        // Show loading state
        submitBtn.disabled = true;
        if (loadingIndicator) loadingIndicator.classList.remove('hidden');
        
        // Prepare form data
        const formData = new FormData(form);
        
        // Send the request
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) throw new Error(data.error);
            
            // Update response container
            if (responseContainer) {
                responseContainer.innerHTML = data.ai_content;
                
                // Rehighlight code blocks
                if (typeof hljs !== 'undefined') {
                    document.querySelectorAll('pre code').forEach(block => {
                        hljs.highlightElement(block);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (responseContainer) {
                responseContainer.innerHTML = `
                    <div class="alert alert-danger">
                        ${error.message}
                    </div>
                `;
            }
        })
        .finally(() => {
            submitBtn.disabled = false;
            if (loadingIndicator) loadingIndicator.classList.add('hidden');
        });
    }
    
    // Preload AI Assistant content when hovering over the link
    const preloadAIAssistant = function() {
        if (aiAssistantLink && !aiAssistantLink.dataset.preloaded) {
            const link = aiAssistantLink.href;
            fetch(link, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                },
                priority: 'low'
            })
            .then(response => {
                if (response.ok) {
                    aiAssistantLink.dataset.preloaded = true;
                }
            })
            .catch(() => {});
        }
    };
    
    // Start preloading when mouse enters the navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.addEventListener('mouseenter', preloadAIAssistant, { once: true });
    }
});