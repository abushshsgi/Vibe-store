// Main JavaScript file for MultiShop E-commerce

document.addEventListener('DOMContentLoaded', function() {
    // Initialize language from session or set default
    const currentLanguage = localStorage.getItem('language') || 'en';
    setLanguage(currentLanguage);
    
    // Add event listeners for language selection
    const languageButtons = document.querySelectorAll('.language-btn');
    if (languageButtons) {
        languageButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const lang = this.getAttribute('data-lang');
                setLanguage(lang);
            });
        });
    }
    
    // Product card hover effects
    const productCards = document.querySelectorAll('.product-card');
    if (productCards) {
        productCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.querySelector('.product-img').style.transform = 'scale(1.1)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.querySelector('.product-img').style.transform = 'scale(1)';
            });
        });
    }
    
    // Button click animation
    const buyButtons = document.querySelectorAll('.btn-buy-now');
    if (buyButtons) {
        buyButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                // Create ripple effect
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                this.appendChild(ripple);
                
                // Get position
                const x = e.clientX - e.target.getBoundingClientRect().left;
                const y = e.clientY - e.target.getBoundingClientRect().top;
                
                // Position the ripple
                ripple.style.left = `${x}px`;
                ripple.style.top = `${y}px`;
                
                // Remove ripple after animation
                setTimeout(() => {
                    ripple.remove();
                }, 800);
            });
        });
    }
    
    // Initialize any tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined') {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Handle wishlist functionality
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');
    if (wishlistButtons) {
        wishlistButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            });
        });
    }
    
    // Search functionality
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                showAlert('Please enter a search term', 'warning');
            }
        });
    }
    
    // Admin dashboard - confirm delete
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    if (alerts) {
        alerts.forEach(alert => {
            setTimeout(() => {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }, 5000);
        });
    }
    
    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    if (forms) {
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }
});

// Function to set the language
function setLanguage(lang) {
    localStorage.setItem('language', lang);
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Update language dropdown if exists
    const languageText = document.getElementById('selected-language');
    if (languageText) {
        languageText.textContent = lang.toUpperCase();
    }
    
    // Set active class for language buttons
    document.querySelectorAll('.language-btn').forEach(btn => {
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertContainer.removeChild(alert);
        }, 150);
    }, 5000);
}

// Function to format price 
function formatPrice(price, currency = '$') {
    return `${currency}${parseFloat(price).toFixed(2)}`;
}

// Add to cart functionality (placeholder for future implementation)
function addToCart(productId, quantity = 1) {
    console.log(`Product ${productId} added to cart with quantity ${quantity}`);
    showAlert('Product added to cart!', 'success');
    // This would typically involve an AJAX call to a backend endpoint
}
