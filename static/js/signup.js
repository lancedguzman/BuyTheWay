document.addEventListener('DOMContentLoaded', function () {

    const userTypeSelect = document.getElementById('id_user_type');
    const sellerField = document.getElementById('seller-additional-field');

    function toggleSellerField() {
        if (userTypeSelect.value === 'S') {
            sellerField.classList.remove('hidden');
        } else {
            sellerField.classList.add('hidden');
        }
    }

    toggleSellerField();
    userTypeSelect.addEventListener('change', toggleSellerField);
});