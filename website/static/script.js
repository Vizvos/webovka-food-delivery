const searchBarContainerEl = document.querySelector(".search-bar-container");
const magnifierEl = document.querySelector(".magnifier");


document.addEventListener('DOMContentLoaded', () => {
    // Inicializace DOM elementů s kontrolou existence
    const elements = {
        weeklymenuContainer: document.querySelector('.weeklyMenu'),
        menuContainer: document.querySelector('.menu'),
        priceFilter: document.getElementById('price-filter'),
        priceValue: document.getElementById('price-value'),
        applyFiltersButton: document.getElementById('apply-filters'),
        searchInput: document.querySelector('.search-bar-container active input[type="text"]'),
        searchButton: document.querySelector('.search-bar-container active button'),
        totalPriceElement: document.getElementById('total-price'),
        finishOrderButton: document.querySelector('#finish-order-btn')
        
    };

    let fullMenu = [];

    magnifierEl.addEventListener("click", () => {
        searchBarContainerEl.classList.toggle("active");
      });

    // Načítání dat z API
    fetch('/api/weeklyMenu')
        .then(response => response.json())
        .then(data => {
            fullMenu = data;
            displayWeeklyMenu(fullMenu);
        })
        .catch(error => console.error('Chyba při načítání menu:', error));

    // Aktualizace UI elementů
    if (elements.cartDataInput) {
        elements.cartDataInput.value = JSON.stringify(CartManager.getCart());
    }

    if (elements.priceFilter) {
        elements.priceFilter.addEventListener('input', () => {
            if (elements.priceValue) {
                elements.priceValue.textContent = `${elements.priceFilter.value} Kč`;
            }
        });
    }

    // Načítání týdenního menu
    async function loadWeeklyMenu() {
        try {
            const response = await fetch('/api/weeklyMenu');
            if (!response.ok) throw new Error('Síťová chyba při načítání týdenního menu');
            const data = await response.json();
            displayWeeklyMenu(data);
        } catch (error) {
            console.error('Chyba při načítání týdenního menu:', error);
        }
    }

    // Zobrazení týdenního menu
    function displayWeeklyMenu(menuData) {
        if (!elements.weeklymenuContainer) return;

        elements.weeklymenuContainer.innerHTML = menuData.map(restaurant => `
            <h2>${restaurant.restaurant_name}</h2>
            <div class="menu-items-container">
                ${restaurant.menu.map(item => `
                    <div class="menu-item">
                        <h3>${item.name}</h3>
                        <img src="${item.image}" alt="${item.name}" class="menu-item-image">
                        <p class="menu-item-price">${item.price} Kč</p>
                        <p>${item.description}</p>
                    </div>
                `).join('')}
            </div>
            <hr>
        `).join('');
    }

    // Filtrování menu
    if (elements.applyFiltersButton) {
        elements.applyFiltersButton.addEventListener('click', () => {
            const maxPrice = parseInt(elements.priceFilter.value) || 0;
            const filteredMenu = fullMenu.filter(item => {
                const price = parseInt(item.price.replace(/[^\d]/g, '')) || 0;
                return price <= maxPrice;
            });
            displayWeeklyMenu(filteredMenu);
        });
    }

    // Vyhledávání v menu
    function searchMenu() {
        if (!elements.searchInput) return;

        const query = elements.searchInput.value.toLowerCase().trim();
        const filteredMenu = fullMenu.filter(item =>
            item.name.toLowerCase().includes(query)
        );
        displayWeeklyMenu(filteredMenu);
    }

    // Event listeners pro vyhledávání
    if (elements.searchButton) {
        elements.searchButton.addEventListener('click', searchMenu);
    }

    if (elements.searchInput) {
        elements.searchInput.addEventListener('keypress', event => {
            if (event.key === 'Enter') {
                searchMenu();
            }
        });
    }

    // Zpracování objednávky
    if (elements.finishOrderButton) {
        elements.finishOrderButton.addEventListener('click', async () => {
            const nameInput = document.querySelector('#name');
            const paymentMethodInput = document.querySelector('#payment-method');

            if (!nameInput || !paymentMethodInput) {
                alert('Chybí potřebné formulářové prvky!');
                return;
            }

            const address = nameInput.value.trim();
            const paymentMethod = paymentMethodInput.value;
            const cart = CartManager.getCart();

            if (!address || !paymentMethod || cart.length === 0) {
                alert('Vyplňte všechny údaje a přidejte položky do košíku!');
                return;
            }

            try {
                const response = await fetch('/create-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cart, address, payment_method: paymentMethod })
                });

                if (!response.ok) throw new Error('Síťová chyba');

                const result = await response.json();
                alert(result.message);
                localStorage.removeItem('cart');
                window.location.href = '/';
            } catch (error) {
                console.error('Chyba při odesílání objednávky:', error);
                alert('Nastala chyba při zpracování objednávky.');
            }
        });
    }

    // Načtení menu při inicializaci
    loadWeeklyMenu();
});

