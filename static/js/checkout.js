// Get form and the hidden payment method input
const checkoutForm = document.getElementById('checkout-form');
const paymentInput = document.getElementById('id_payment_method');
const modal = document.getElementById('qrModal');
const modalTitle = document.getElementById('modalTitle');

function openModal(method) {
    // Set the hidden input value in the form
    if (paymentInput) paymentInput.value = method;

    // Hide QR codes first
    const allQrs = document.querySelectorAll('.qr-code');
    allQrs.forEach(qr => qr.style.display = 'none');

    // Show requested QR along with title
    let qrsToShow;
    if (method === 'gcash') {
        qrsToShow = document.querySelectorAll('.qr-gcash');
        if (modalTitle) modalTitle.innerText = 'Scan GCash QR';
    } else if (method === 'maya') {
        qrsToShow = document.querySelectorAll('.qr-maya');
        if (modalTitle) modalTitle.innerText = 'Scan Maya QR';
    } else if (method === 'bank') {
        qrsToShow = document.querySelectorAll('.qr-bank');
        if (modalTitle) modalTitle.innerText = 'Scan Bank QR';
    }
    
    if (qrsToShow) {
        qrsToShow.forEach(qr => qr.style.display = 'block');
    }

    // 4. Show the modal
    if (modal) modal.style.display = 'flex';
}

function closeModal() {
    if (modal) modal.style.display = 'none';
}

function submitCheckoutForm() {
    // Check if user now typed an address before submitting
    const addressInput = document.getElementById('id_address');
    if (addressInput && !addressInput.value) {
        alert("Please enter a delivery address first!");
        closeModal();
        addressInput.focus();
        return;
    }
    
    // Submit form
    if (checkoutForm) checkoutForm.submit();
}