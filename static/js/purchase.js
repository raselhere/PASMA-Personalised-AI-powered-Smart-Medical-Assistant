// Cart functionality
let cart = []
let cartTotal = 0
let medicines = []
let currentPage = 1
const itemsPerPage = 12

// Initialize cart from localStorage if available
document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("cart")) {
    cart = JSON.parse(localStorage.getItem("cart"))
    updateCartUI()
  }

  // Fetch medicines from JSON file
  fetch("/purchase_medicines")
    .then((response) => {
      console.log("Response status:", response.status)
      return response.json()
    })
    .then((data) => {
      console.log("Medicines data loaded:", data)
      medicines = data
      displayMedicines(medicines)
      setupPagination(medicines)
    })
    .catch((error) => {
      console.error("Error loading medicines:", error)
      document.getElementById("productGrid").innerHTML =
        '<div class="col-12 text-center"><p>Failed to load medicines. Please try again later.</p></div>'
    })
})

// Display medicines with pagination
function displayMedicines(medicinesList) {
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentMedicines = medicinesList.slice(startIndex, endIndex)

  const productGrid = document.getElementById("productGrid")
  productGrid.innerHTML = ""

  if (currentMedicines.length === 0) {
    productGrid.innerHTML = '<div class="col-12 text-center"><p>No medicines found matching your criteria.</p></div>'
    return
  }

  currentMedicines.forEach((medicine) => {
    const productCard = document.createElement("div")
    productCard.className = "col-md-4 col-sm-6 mb-4 product-item"
    productCard.setAttribute("data-name", medicine.name.toLowerCase())
    productCard.setAttribute("data-category", medicine.category.toLowerCase())
    productCard.setAttribute("data-price", medicine.price)

    // Use default medicine icon for all medicines
    const defaultMedicineIcon = "/static/medicine-icon.png"

    productCard.innerHTML = `
            <div class="product-card">
                <div class="product-image">
                    <img src="${defaultMedicineIcon}" alt="${medicine.name}" onerror="this.src='${defaultMedicineIcon}'">
                </div>
                <div class="product-details">
                    <div class="product-category">${medicine.category}</div>
                    <h3 class="product-name">${medicine.name}</h3>
                    <p class="product-description">${medicine.description}</p>
                    <div class="product-price">$${medicine.price.toFixed(2)}</div>
                    <div class="product-company">${medicine.company}</div>
                    <div class="product-actions">
                        <button class="btn-add-to-cart" onclick="addToCart('${medicine.name}', ${medicine.price}, '${defaultMedicineIcon}')">
                            <i class="fas fa-cart-plus"></i> Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        `

    productGrid.appendChild(productCard)
  })
}

// Setup pagination
function setupPagination(medicinesList) {
  const totalPages = Math.ceil(medicinesList.length / itemsPerPage)
  const pagination = document.getElementById("pagination")
  pagination.innerHTML = ""

  // Previous button
  const prevLi = document.createElement("li")
  prevLi.className = `page-item ${currentPage === 1 ? "disabled" : ""}`
  prevLi.innerHTML = `
        <a class="page-link" href="#" aria-label="Previous" ${currentPage !== 1 ? 'onclick="changePage(' + (currentPage - 1) + ')"' : ""}>
            <i class="fas fa-chevron-left"></i>
        </a>
    `
  pagination.appendChild(prevLi)

  // Page numbers
  for (let i = 1; i <= totalPages; i++) {
    const pageLi = document.createElement("li")
    pageLi.className = `page-item ${i === currentPage ? "active" : ""}`
    pageLi.innerHTML = `<a class="page-link" href="#" onclick="changePage(${i})">${i}</a>`
    pagination.appendChild(pageLi)
  }

  // Next button
  const nextLi = document.createElement("li")
  nextLi.className = `page-item ${currentPage === totalPages ? "disabled" : ""}`
  nextLi.innerHTML = `
        <a class="page-link" href="#" aria-label="Next" ${currentPage !== totalPages ? 'onclick="changePage(' + (currentPage + 1) + ')"' : ""}>
            <i class="fas fa-chevron-right"></i>
        </a>
    `
  pagination.appendChild(nextLi)
}

// Change page
function changePage(page) {
  currentPage = page
  displayMedicines(medicines)
  setupPagination(medicines)
  window.scrollTo(0, 0)
}

// Add item to cart
function addToCart(name, price, image) {
  // Check if item already exists in cart
  const existingItem = cart.find((item) => item.name === name)

  if (existingItem) {
    existingItem.quantity += 1
  } else {
    cart.push({
      name: name,
      price: price,
      image: image,
      quantity: 1,
    })
  }

  // Save cart to localStorage
  localStorage.setItem("cart", JSON.stringify(cart))

  // Update cart UI
  updateCartUI()

  // Show notification
  showNotification(`${name} added to cart!`)
}

// Remove item from cart
function removeFromCart(index) {
  cart.splice(index, 1)
  localStorage.setItem("cart", JSON.stringify(cart))
  updateCartUI()
}

// Update item quantity
function updateQuantity(index, change) {
  cart[index].quantity += change

  if (cart[index].quantity < 1) {
    cart[index].quantity = 1
  }

  localStorage.setItem("cart", JSON.stringify(cart))
  updateCartUI()
}

// Update cart UI
function updateCartUI() {
  const cartItemsElement = document.getElementById("cartItems")
  const cartCountElement = document.getElementById("cartCount")
  const cartTotalElement = document.getElementById("cartTotal")
  const emptyCartElement = document.getElementById("emptyCart")

  // Clear current items
  cartItemsElement.innerHTML = ""

  // Calculate total
  cartTotal = 0

  if (cart.length === 0) {
    // Show empty cart message
    const emptyCartDiv = document.createElement("div")
    emptyCartDiv.className = "empty-cart"
    emptyCartDiv.id = "emptyCart"
    emptyCartDiv.innerHTML = `
            <i class="fas fa-shopping-basket"></i>
            <p>Your cart is empty</p>
        `
    cartItemsElement.appendChild(emptyCartDiv)
    cartCountElement.textContent = "0"
    cartTotalElement.textContent = "$0.00"
  } else {
    // Add each item to cart
    cart.forEach((item, index) => {
      const itemTotal = item.price * item.quantity
      cartTotal += itemTotal

      // Use default medicine icon for cart items
      const defaultMedicineIcon = "/static/medicine-icon.png"

      const cartItemElement = document.createElement("div")
      cartItemElement.className = "cart-item"
      cartItemElement.innerHTML = `
                <img src="${defaultMedicineIcon}" alt="${item.name}" class="cart-item-img" onerror="this.src='${defaultMedicineIcon}'">
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${item.price.toFixed(2)}</div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn" onclick="updateQuantity(${index}, -1)">-</button>
                        <input type="text" class="quantity-input" value="${item.quantity}" readonly>
                        <button class="quantity-btn" onclick="updateQuantity(${index}, 1)">+</button>
                    </div>
                </div>
                <div class="cart-item-remove" onclick="removeFromCart(${index})">
                    <i class="fas fa-trash"></i>
                </div>
            `

      cartItemsElement.appendChild(cartItemElement)
    })

    // Update cart count and total
    cartCountElement.textContent = cart.reduce((total, item) => total + item.quantity, 0)
    cartTotalElement.textContent = "$" + cartTotal.toFixed(2)
  }
}

// Show notification
function showNotification(message) {
  // Create notification element
  const notification = document.createElement("div")
  notification.className = "toast show"
  notification.style.position = "fixed"
  notification.style.bottom = "20px"
  notification.style.right = "20px"
  notification.style.backgroundColor = "var(--primary-color)"
  notification.style.color = "white"
  notification.style.padding = "10px 20px"
  notification.style.borderRadius = "5px"
  notification.style.zIndex = "9999"
  notification.style.boxShadow = "0 5px 15px rgba(0, 0, 0, 0.1)"
  notification.innerHTML = message

  // Add to body
  document.body.appendChild(notification)

  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove("show")
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 300)
  }, 3000)
}

// Search medicines
function searchMedicines() {
  const searchInput = document.getElementById("medicineSearch").value.toLowerCase()
  const filteredMedicines = medicines.filter(
    (medicine) =>
      medicine.name.toLowerCase().includes(searchInput) ||
      medicine.category.toLowerCase().includes(searchInput) ||
      medicine.description.toLowerCase().includes(searchInput) ||
      medicine.company.toLowerCase().includes(searchInput),
  )

  currentPage = 1
  displayMedicines(filteredMedicines)
  setupPagination(filteredMedicines)
}

// Filter medicines
function filterMedicines() {
  let filteredMedicines = [...medicines]

  // Category filters
  const categoryFilters = []
  if (document.getElementById("categoryPain").checked) categoryFilters.push("pain relief")
  if (document.getElementById("categoryAntibiotics").checked) categoryFilters.push("antibiotics")
  if (document.getElementById("categoryCardiac").checked) categoryFilters.push("cardiac care")
  if (document.getElementById("categoryDiabetes").checked) categoryFilters.push("diabetes care")

  if (categoryFilters.length > 0) {
    filteredMedicines = filteredMedicines.filter((medicine) =>
      categoryFilters.includes(medicine.category.toLowerCase()),
    )
  }

  // Price range filter
  const minPrice = Number.parseFloat(document.getElementById("minPrice").value) || 0
  const maxPrice = Number.parseFloat(document.getElementById("maxPrice").value) || Number.MAX_VALUE

  filteredMedicines = filteredMedicines.filter((medicine) => medicine.price >= minPrice && medicine.price <= maxPrice)

  currentPage = 1
  displayMedicines(filteredMedicines)
  setupPagination(filteredMedicines)
}
