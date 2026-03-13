function increaseQty() {
    const display = document.getElementById("quantity-display");
    const input = document.getElementById("quantity-input");
    
    if (!input || !display) return;

    // Get the max stock from the data attribute
    const max = parseInt(input.getAttribute("data-max-stock")) || 1;
    let value = parseInt(input.value) || 1;
    
    if (value < max) {
        value++;
        input.value = value;
        display.innerText = value;
    }
    console.log("Current Qty:", input.value);
}

function decreaseQty() {
    const display = document.getElementById("quantity-display");
    const input = document.getElementById("quantity-input");
    
    if (!input || !display) return;

    let value = parseInt(input.value) || 1;
    
    if (value > 1) {
        value--;
        input.value = value;
        display.innerText = value;
    }
    console.log("Current Qty:", input.value);
}