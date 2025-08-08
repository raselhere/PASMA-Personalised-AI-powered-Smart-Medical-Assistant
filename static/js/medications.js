// Function to handle medication deletion
function deleteMedication(medicationId) {
  if (confirm("Are you sure you want to delete this medication?")) {
    // Create form data
    const formData = new FormData()
    formData.append("medication_id", medicationId)

    // Send request to server
    fetch("/delete_medication", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Show success message
          alert("Medication deleted successfully")
          // Reload page to reflect changes
          window.location.reload()
        } else {
          alert("Failed to delete medication: " + (data.message || "Unknown error"))
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("An error occurred while deleting the medication")
      })
  }
}

// Update any references to medicines.json in the JavaScript file
// Function to load medications
function loadMedications() {
  console.log("Loading medications...")
  fetch("/get_medications")
    .then((response) => {
      console.log("Response status:", response.status)
      return response.json()
    })
    .then((data) => {
      console.log("Medications data:", data)
      const medicationsList = document.getElementById("medicationsList")
      const medicationsModalList = document.getElementById("medicationsModalList")

      if (!medicationsList) {
        console.error("Medications list element not found")
        return
      }

      if (data.success && data.medications && data.medications.length > 0) {
        console.log(`Found ${data.medications.length} medications`)
        let html = ""

        data.medications.forEach((med) => {
          const endDateText = med.end_date ? new Date(med.end_date).toLocaleDateString() : "Ongoing"

          html += `
            <div class="medication-item">
                <div class="medication-info">
                    <div class="medication-name">${med.name} ${med.dosage}</div>
                    <div class="medication-schedule">${med.frequency} | ${new Date(med.start_date).toLocaleDateString()} - ${endDateText}</div>
                    <div class="text-muted small">${med.instructions || ""}</div>
                </div>
                <div class="medication-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="editMedication('${med.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteMedication('${med.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
          `
        })

        medicationsList.innerHTML = html

        // Also update the modal list
        if (medicationsModalList) {
          medicationsModalList.innerHTML = html
        }
      } else {
        console.log("No medications found or data.success is false")
        medicationsList.innerHTML = `
          <div class="no-appointments-message">
              <i class="fas fa-info-circle me-2"></i> You don't have any medications yet.
          </div>
        `

        if (medicationsModalList) {
          medicationsModalList.innerHTML = medicationsList.innerHTML
        }
      }
    })
    .catch((error) => {
      console.error("Error loading medications:", error)
    })
}

// Function to edit medication (placeholder for now)
function editMedication(medicationId) {
  // In a real app, this would open a modal with the medication details
  alert(`Edit medication ${medicationId} - This feature is coming soon`)
}

// Function to handle form submission
function submitMedicationForm(event) {
  event.preventDefault()
  console.log("Submitting medication form...")

  const form = document.getElementById("addMedicationForm")
  const formData = new FormData(form)

  // Log form data for debugging
  for (const [key, value] of formData.entries()) {
    console.log(`${key}: ${value}`)
  }

  fetch("/add_medication", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      console.log("Response status:", response.status)
      if (response.redirected) {
        window.location.href = response.url
        return
      }
      return response.json()
    })
    .then((data) => {
      if (data && data.success) {
        alert("Medication added successfully!")
        // Close the modal
        const modalElement = document.getElementById("addMedicationModal")
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) modal.hide()
        // Reload medications
        loadMedications()
      } else if (data) {
        alert("Failed to add medication: " + (data.message || "Unknown error"))
      }
    })
    .catch((error) => {
      console.error("Error adding medication:", error)
      // If there's an error but the page was redirected, it might be a success
      if (window.location.href.includes("patient-appointment")) {
        loadMedications()
      } else {
        alert("An error occurred while adding the medication. Please try again.")
      }
    })
}

// Load medications when the page loads
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing medication functionality")
  loadMedications()

  // Add event listener to the form
  const form = document.getElementById("addMedicationForm")
  if (form) {
    console.log("Found medication form, adding submit event listener")
    form.addEventListener("submit", submitMedicationForm)
  } else {
    console.error("Medication form not found")
  }
})
