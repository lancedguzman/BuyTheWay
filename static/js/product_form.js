document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("product-form");
    if (!form) return;


    const imageInputId = form.dataset.imageInput;
    const groupPaymentId = form.dataset.groupPayment;
    const groupPriceId = form.dataset.groupPrice;
    const hasImage = form.dataset.hasImage === "true";
    const imageUrl = form.dataset.imageUrl;

    const imageInput = document.getElementById(imageInputId);
    const previewImg = document.getElementById("image-preview");
    const cameraIcon = document.getElementById("camera-icon");
    const previewContainer = document.getElementById("preview-container");

    if (imageInput) {
        imageInput.addEventListener("change", function() {
            const file = this.files[0];
            
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = "block";
                    }
                    if (cameraIcon) cameraIcon.style.display = "none";
                    if (previewContainer) previewContainer.style.border = "none"; 
                }
                reader.readAsDataURL(file);
            } else {
                if (hasImage) {
                    if (previewImg) {
                        previewImg.src = imageUrl;
                        previewImg.style.display = "block";
                    }
                    if (cameraIcon) cameraIcon.style.display = "none";
                    if (previewContainer) previewContainer.style.border = "none";
                } else {
                    if (previewImg) {
                        previewImg.src = "#";
                        previewImg.style.display = "none";
                    }
                    if (cameraIcon) cameraIcon.style.display = "block";
                    if (previewContainer) previewContainer.style.border = "0.2vw dashed #d4d4d4";
                }
            }
        });
    }


    const groupPaymentCheckbox = document.getElementById(groupPaymentId);
    const groupPriceInput = document.getElementById(groupPriceId);

    function toggleGroupPrice() {
        if (groupPaymentCheckbox.checked) {
            groupPriceInput.disabled = false;
            groupPriceInput.style.backgroundColor = "#f4f4f4"; 
            groupPriceInput.style.cursor = "text";
        } else {
            groupPriceInput.disabled = true;
            groupPriceInput.value = ""; // Clear out the value
            groupPriceInput.style.backgroundColor = "#e0e0e0"; // Greyed out
            groupPriceInput.style.cursor = "not-allowed";
        }
    }

    if (groupPaymentCheckbox && groupPriceInput) {
        groupPaymentCheckbox.addEventListener("change", toggleGroupPrice);
        // Run once on load to set the initial state (especially useful for Edit mode)
        toggleGroupPrice(); 
    }
});