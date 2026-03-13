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