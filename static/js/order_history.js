document.addEventListener("DOMContentLoaded", function() {
    const tabs = document.querySelectorAll('.tab');
    const cards = document.querySelectorAll('.order-card');
    const emptyMessage = document.getElementById('emptyMessage');
    
    const statusMap = {
        'Pending': 'P',
        'Confirmed': 'C',
        'Shipping': 'S',
        'Completed': 'CP',
        'Cancelled': 'X'
    };

    function filterOrders(statusText) {
        const targetStatus = statusMap[statusText];
        let itemsFound = false;
        
        cards.forEach(card => {
            if (card.getAttribute('data-status') === targetStatus) {
                card.style.display = 'block';
                itemsFound = true;
            } else {
                card.style.display = 'none';
            }
        });

        if (!itemsFound && cards.length > 0) {
            if (emptyMessage) emptyMessage.style.display = 'block';
        } else {
            if (emptyMessage) emptyMessage.style.display = 'none';
        }
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => {
                t.classList.remove('active');
                t.classList.add('inactive');
            });
            
            tab.classList.remove('inactive');
            tab.classList.add('active');
            
            filterOrders(tab.innerText.trim());
        });
    });

    const initialTab = document.querySelector('.tab.active');
    if(initialTab) {
        filterOrders(initialTab.innerText.trim());
    }
});