function scrollCategories(direction) {
    const container = document.getElementById('categoryContainer');
    const scrollAmount = 300; // pixels to scroll
    container.scrollLeft += direction * scrollAmount;
}

function showMoreProducts() {
    const hiddenProducts = document.querySelectorAll('.product-item.hidden');
    
    // Show all hidden products at once
    hiddenProducts.forEach(product => {
        product.classList.remove('hidden');
    });
    
    // Hide the button after showing all products
    const seeMoreContainer = document.querySelector('.see-more-container');
    if (seeMoreContainer) {
        seeMoreContainer.style.display = 'none';
    }
}

function filterProducts(category) {
    const products = document.querySelectorAll('.product-item');
    products.forEach(product => {
        if (category === 'ALL' || product.classList.contains(category)) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
    
    // Update active button styling
    const buttons = document.querySelectorAll('.category-btn');
    buttons.forEach(button => {
        if (button.id === category || category === 'ALL' && button.id === 'ALL') {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}