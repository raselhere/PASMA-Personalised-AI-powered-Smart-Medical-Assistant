// List of valid symptoms that the backend can handle
const validSymptoms = [
  "itching",
  "skin_rash",
  "nodal_skin_eruptions",
  "continuous_sneezing",
  "shivering",
  "chills",
  "joint_pain",
  "stomach_pain",
  "acidity",
  "ulcers_on_tongue",
  "muscle_wasting",
  "vomiting",
  "burning_micturition",
  "spotting_ urination",
  "fatigue",
  "weight_gain",
  "anxiety",
  "cold_hands_and_feets",
  "mood_swings",
  "weight_loss",
  "restlessness",
  "lethargy",
  "patches_in_throat",
  "irregular_sugar_level",
  "cough",
  "high_fever",
  "sunken_eyes",
  "breathlessness",
  "sweating",
  "dehydration",
  "indigestion",
  "headache",
  "yellowish_skin",
  "dark_urine",
  "nausea",
  "loss_of_appetite",
  "pain_behind_the_eyes",
  "back_pain",
  "constipation",
  "abdominal_pain",
  "diarrhoea",
  "mild_fever",
  "yellow_urine",
  "yellowing_of_eyes",
  "acute_liver_failure",
  "fluid_overload",
  "swelling_of_stomach",
  "swelled_lymph_nodes",
  "malaise",
  "blurred_and_distorted_vision",
  "phlegm",
  "throat_irritation",
  "redness_of_eyes",
  "sinus_pressure",
  "runny_nose",
  "congestion",
  "chest_pain",
  "weakness_in_limbs",
  "fast_heart_rate",
  "pain_during_bowel_movements",
  "pain_in_anal_region",
  "bloody_stool",
  "irritation_in_anus",
  "neck_pain",
  "dizziness",
  "cramps",
  "bruising",
  "obesity",
  "swollen_legs",
  "swollen_blood_vessels",
  "puffy_face_and_eyes",
  "enlarged_thyroid",
  "brittle_nails",
  "swollen_extremeties",
  "excessive_hunger",
  "extra_marital_contacts",
  "drying_and_tingling_lips",
  "slurred_speech",
  "knee_pain",
  "hip_joint_pain",
  "muscle_weakness",
  "stiff_neck",
  "swelling_joints",
  "movement_stiffness",
  "spinning_movements",
  "loss_of_balance",
  "unsteadiness",
  "weakness_of_one_body_side",
  "loss_of_smell",
  "bladder_discomfort",
  "foul_smell_of urine",
  "continuous_feel_of_urine",
  "passage_of_gases",
  "internal_itching",
  "toxic_look_(typhos)",
  "depression",
  "irritability",
  "muscle_pain",
  "altered_sensorium",
  "red_spots_over_body",
  "belly_pain",
  "abnormal_menstruation",
  "dischromic _patches",
  "watering_from_eyes",
  "increased_appetite",
  "polyuria",
  "family_history",
  "mucoid_sputum",
  "rusty_sputum",
  "lack_of_concentration",
  "visual_disturbances",
  "receiving_blood_transfusion",
  "receiving_unsterile_injections",
  "coma",
  "stomach_bleeding",
  "distention_of_abdomen",
  "history_of_alcohol_consumption",
  "fluid_overload.1",
  "blood_in_sputum",
  "prominent_veins_on_calf",
  "palpitations",
  "painful_walking",
  "pus_filled_pimples",
  "blackheads",
  "scurring",
  "skin_peeling",
  "silver_like_dusting",
  "small_dents_in_nails",
  "inflammatory_nails",
  "blister",
  "red_sore_around_nose",
  "yellow_crust_ooze",
]

// Function to validate symptoms input
function validateSymptoms(input) {
  // Split the input by commas and trim each symptom
  const inputSymptoms = input.split(",").map((symptom) => symptom.trim().toLowerCase())

  // Check if all symptoms are valid
  const invalidSymptoms = inputSymptoms.filter((symptom) => !validSymptoms.includes(symptom))

  return {
    valid: invalidSymptoms.length === 0 && inputSymptoms.length > 0,
    invalidSymptoms: invalidSymptoms,
  }
}

// Function to show symptom suggestions
function showSymptomSuggestions(input) {
  const searchTerm = input.toLowerCase()
  if (searchTerm.length < 2) return []

  return validSymptoms.filter((symptom) => symptom.includes(searchTerm)).slice(0, 5) // Limit to 5 suggestions
}

// Initialize the symptom form validation
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector('form[action="/predict"]')
  const symptomsInput = document.getElementById("symptoms")
  const suggestionsList = document.createElement("div")
  suggestionsList.className = "list-group mt-2"
  suggestionsList.id = "symptomSuggestions"
  symptomsInput.parentNode.insertBefore(suggestionsList, symptomsInput.nextSibling)

  // Create a feedback element for validation messages
  const feedbackElement = document.createElement("div")
  feedbackElement.className = "invalid-feedback"
  feedbackElement.style.display = "none"
  symptomsInput.parentNode.insertBefore(feedbackElement, suggestionsList.nextSibling)

  // Add input event listener for suggestions
  symptomsInput.addEventListener("input", function () {
    const value = this.value
    const lastSymptom = value.split(",").pop().trim()

    if (lastSymptom.length >= 2) {
      const suggestions = showSymptomSuggestions(lastSymptom)

      if (suggestions.length > 0) {
        suggestionsList.innerHTML = ""
        suggestions.forEach((suggestion) => {
          const item = document.createElement("a")
          item.href = "#"
          item.className = "list-group-item list-group-item-action"
          item.textContent = suggestion
          item.addEventListener("click", (e) => {
            e.preventDefault()
            const currentValue = symptomsInput.value
            const symptoms = currentValue.split(",")
            symptoms.pop() // Remove the last incomplete symptom
            symptoms.push(suggestion) // Add the selected suggestion
            symptomsInput.value = symptoms.join(", ")
            suggestionsList.innerHTML = ""
            symptomsInput.focus()
          })
          suggestionsList.appendChild(item)
        })
        suggestionsList.style.display = "block"
      } else {
        suggestionsList.style.display = "none"
      }
    } else {
      suggestionsList.style.display = "none"
    }

    // Hide validation message when input changes
    feedbackElement.style.display = "none"
    symptomsInput.classList.remove("is-invalid")
  })

  // Add form submit event listener
  form.addEventListener("submit", (event) => {
    const value = symptomsInput.value.trim()
    const validation = validateSymptoms(value)

    if (!validation.valid) {
      event.preventDefault()

      // Show validation message
      if (value === "") {
        feedbackElement.textContent = "Please enter at least one symptom."
      } else {
        feedbackElement.textContent = `Invalid symptoms: ${validation.invalidSymptoms.join(", ")}. Please enter valid symptoms.`
      }

      feedbackElement.style.display = "block"
      symptomsInput.classList.add("is-invalid")

      // Create a Bootstrap alert
      const alertDiv = document.createElement("div")
      alertDiv.className = "alert alert-warning alert-dismissible fade show mt-3"
      alertDiv.setAttribute("role", "alert")

      const message =
        value === ""
          ? "Please enter at least one symptom."
          : `The following symptoms are not recognized: ${validation.invalidSymptoms.join(", ")}. Please enter valid symptoms.`

      alertDiv.innerHTML = `
        <strong>Invalid Symptoms!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `

      // Insert the alert before the form
      form.parentNode.insertBefore(alertDiv, form)

      // Scroll to the alert
      alertDiv.scrollIntoView({ behavior: "smooth", block: "center" })

      // Auto-dismiss after 5 seconds
      const bsAlert = new bootstrap.Alert(alertDiv)
      setTimeout(() => {
        bsAlert.close()
      }, 5000)
    }
  })

  // Hide suggestions when clicking outside
  document.addEventListener("click", (e) => {
    if (e.target !== symptomsInput && e.target !== suggestionsList) {
      suggestionsList.style.display = "none"
    }
  })
})
