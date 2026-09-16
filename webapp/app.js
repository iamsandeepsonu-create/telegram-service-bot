// Telegram WebApp Client Integration
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
}

let allServices = [];
let currentCurrency = 'INR';
let usdRate = 85.0;
let selectedService = null;

// DOM Elements
const servicesListEl = document.getElementById('servicesList');
const searchInput = document.getElementById('searchInput');
const currencyToggleBtn = document.getElementById('currencyToggleBtn');
const currencyFlag = document.getElementById('currencyFlag');
const currencyLabel = document.getElementById('currencyLabel');

const modal = document.getElementById('serviceModal');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalTitle = document.getElementById('modalTitle');
const modalPrice = document.getElementById('modalPrice');
const modalDuration = document.getElementById('modalDuration');
const modalDesc = document.getElementById('modalDesc');
const orderRequirements = document.getElementById('orderRequirements');
const modalOrderSubmitBtn = document.getElementById('modalOrderSubmitBtn');
const modalStatusMsg = document.getElementById('modalStatusMsg');

// Format Price
function formatPrice(priceInr) {
  if (currentCurrency === 'USD') {
    const usd = priceInr / usdRate;
    return `$${usd.toFixed(2)}`;
  }
  return `₹${Number(priceInr).toLocaleString('en-IN')}`;
}

// Render Services Button List (Matches reference image: Solid Blue Buttons)
function renderServices(services) {
  if (!services || services.length === 0) {
    servicesListEl.innerHTML = '<div class="loading-box"><p>No services found.</p></div>';
    return;
  }

  servicesListEl.innerHTML = '';
  services.forEach((service) => {
    const btn = document.createElement('button');
    btn.className = 'service-item-btn';
    
    const titleSpan = document.createElement('span');
    titleSpan.className = 'service-title-text';
    titleSpan.textContent = service.name.toUpperCase();

    btn.appendChild(titleSpan);
    btn.addEventListener('click', () => openModal(service));
    servicesListEl.appendChild(btn);
  });
}

// Open Order Modal
function openModal(service) {
  selectedService = service;
  modalTitle.textContent = service.name.toUpperCase();
  modalPrice.textContent = formatPrice(service.price);
  modalDuration.textContent = `⏱️ ${service.duration}`;
  modalDesc.textContent = service.description;
  orderRequirements.value = '';
  modalStatusMsg.className = 'modal-status hidden';
  modalStatusMsg.textContent = '';
  modalOrderSubmitBtn.disabled = false;
  modalOrderSubmitBtn.textContent = '⚡ PROCEED TO ORDER';
  modal.classList.remove('hidden');
}

// Close Modal
function closeModal() {
  modal.classList.add('hidden');
  selectedService = null;
}

modalCloseBtn.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});

// Toggle Currency (INR <-> USD)
currencyToggleBtn.addEventListener('click', () => {
  if (currentCurrency === 'INR') {
    currentCurrency = 'USD';
    currencyFlag.textContent = '🌍';
    currencyLabel.textContent = 'USD ($)';
  } else {
    currentCurrency = 'INR';
    currencyFlag.textContent = '🇮🇳';
    currencyLabel.textContent = 'INR (₹)';
  }
  if (selectedService) {
    modalPrice.textContent = formatPrice(selectedService.price);
  }
});

// Live Search Filter
function getFilteredServices() {
  const query = searchInput.value.toLowerCase().trim();
  if (!query) return allServices;
  return allServices.filter(s => 
    s.name.toLowerCase().includes(query) || 
    s.description.toLowerCase().includes(query)
  );
}

searchInput.addEventListener('input', () => {
  renderServices(getFilteredServices());
});

// Order Submission
modalOrderSubmitBtn.addEventListener('click', async () => {
  if (!selectedService) return;

  const requirements = orderRequirements.value.trim();
  if (requirements.length < 3) {
    modalStatusMsg.className = 'modal-status error';
    modalStatusMsg.textContent = '⚠️ Please enter brief project instructions.';
    return;
  }

  modalOrderSubmitBtn.disabled = true;
  modalOrderSubmitBtn.textContent = '⏳ Processing...';

  const user = tg?.initDataUnsafe?.user || { id: 0, first_name: 'Telegram User' };

  try {
    const response = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user.id,
        username: user.username || null,
        full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'Telegram User',
        service_id: selectedService.id,
        requirements: requirements,
        currency: currentCurrency
      })
    });

    const result = await response.json();

    if (result.success) {
      modalStatusMsg.className = 'modal-status success';
      modalStatusMsg.textContent = `🎉 Order #${result.order_id} Placed! Details sent in your chat.`;
      
      if (tg) {
        tg.HapticFeedback?.notificationOccurred('success');
        setTimeout(() => {
          tg.close();
        }, 1800);
      }
    } else {
      throw new Error(result.error || 'Failed to place order.');
    }
  } catch (err) {
    modalStatusMsg.className = 'modal-status error';
    modalStatusMsg.textContent = `❌ ${err.message}`;
    modalOrderSubmitBtn.disabled = false;
    modalOrderSubmitBtn.textContent = '⚡ PROCEED TO ORDER';
  }
});

// Initial Data Load
async function initApp() {
  try {
    const servicesRes = await fetch('/api/services');
    const servicesData = await servicesRes.json();
    allServices = servicesData.services || [];
    renderServices(allServices);
  } catch (err) {
    console.error('Failed to load services:', err);
    servicesListEl.innerHTML = '<div class="loading-box"><p>⚠️ Failed to load services. Please retry.</p></div>';
  }
}

initApp();
