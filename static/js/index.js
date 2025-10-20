document.addEventListener("DOMContentLoaded", function () {
  const missionModal = document.getElementById("missionModal");
  const submitResponseButton = document.getElementById("submit-response");
  const responseField = document.getElementById("mission-response");
  const hiddenMissionIdField = document.getElementById("hidden-mission-id");
  const validatedMessage = document.getElementById("mission-validated-message");
  const responseSection = document.getElementById("mission-response-section");

  // Timer jusqu'à vendredi 31
  const countdownElement = document.getElementById("countdown");
  const targetDate = new Date("2025-10-31T23:59:59"); // Vendredi 31 octobre 2025
  function updateCountdown() {
    const now = new Date();
    const diff = targetDate - now;

    if (diff <= 0) {
      countdownElement.textContent = "Temps écoulé !";
      return;
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    countdownElement.textContent = `${days}j ${hours}h ${minutes}m ${seconds}s`;
  }
  setInterval(updateCountdown, 1000);
  updateCountdown();

  // Track current mission state in the modal
  let missionState = { validated: false, attempts: 0 };

  if (missionModal) {
    missionModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      const missionId = button.getAttribute("data-mission-id");

      console.log("Mission ID (show modal):", missionId);
      hiddenMissionIdField.value = missionId;

      const modalBody = missionModal.querySelector(".modal-body");
      const missionIdElement = modalBody.querySelector("#mission-id");
      if (missionIdElement) {
        missionIdElement.textContent = missionId;
      } else {
        console.warn("Élément #mission-id introuvable dans la modale.");
      }

      // Reset UI state for each open
      missionState = { validated: false, attempts: 0 };
      if (responseSection) responseSection.style.display = "";
      responseField.value = "";
      responseField.disabled = false;
      submitResponseButton.style.display = "";
      submitResponseButton.disabled = false;
      validatedMessage.style.display = "none";
      modalBody.querySelector("#mission-attempts").textContent = "0";
      modalBody.querySelector("#mission-validated").textContent = "Non";

      // Replace previous single fetch with combined info + status
      Promise.all([
        fetch(`/get_mission_info/${missionId}`).then((r) => {
          if (!r.ok) throw new Error("Erreur réseau get_mission_info");
          return r.json();
        }),
        fetch(`/mission_status?mission_id=${missionId}`).then((r) => {
          if (!r.ok) throw new Error("Erreur réseau mission_status");
          return r.json();
        }),
      ])
        .then(([missionInfo, status]) => {
          if (missionInfo.success) {
            const modalTitle = missionModal.querySelector(".modal-title");
            modalTitle.textContent = `Mission ${missionId}`;
            modalBody.querySelector("#mission-description").textContent =
              missionInfo.mission.description || "Aucune description";

            // Cacher les champs de réponse si non requis
            const requiresAnswer = !!missionInfo.mission.requires_answer;
            if (!requiresAnswer) {
              if (responseSection) responseSection.style.display = "none";
              submitResponseButton.style.display = "none";
            }
          }
          if (status.success) {
            missionState.validated = !!status.validated;
            missionState.attempts = status.attempts || 0;

            modalBody.querySelector("#mission-attempts").textContent = String(
              missionState.attempts
            );
            modalBody.querySelector("#mission-validated").textContent =
              missionState.validated ? "Oui" : "Non";

            if (missionState.validated) {
              responseField.disabled = true;
              submitResponseButton.disabled = true;
              validatedMessage.style.display = "block";
            }
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  }

  if (submitResponseButton) {
    submitResponseButton.addEventListener("click", function () {
      const missionId = hiddenMissionIdField.value;
      const response = responseField.value.trim();

      console.log("Mission ID envoyé (submit):", missionId);
      console.log("Réponse envoyée:", response);

      // Block client-side if already validated
      if (missionState.validated) {
        alert("Cette mission est déjà validée.");
        return;
      }

      if (!missionId || missionId === "null") {
        alert("Erreur : ID de mission invalide.");
        return;
      }

      if (!response) {
        alert("Veuillez entrer une réponse.");
        return;
      }

      fetch("/submit_attempt", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `mission_id=${missionId}&response=${encodeURIComponent(
          response
        )}`,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Reflect validated state in UI
            missionState.validated = true;
            missionState.attempts = data.attempts ?? missionState.attempts + 1;

            const missionValidated =
              document.getElementById("mission-validated");
            const missionAttempts = document.getElementById("mission-attempts");
            if (missionValidated) missionValidated.textContent = "Oui";
            if (missionAttempts)
              missionAttempts.textContent = String(missionState.attempts);

            alert(data.message);
            responseField.value = "";
            responseField.disabled = true;
            submitResponseButton.disabled = true;
            validatedMessage.style.display = "block";

            const tdElement = document.querySelector(
              `td[data-mission-id="${missionId}"]`
            );
            if (tdElement) {
              tdElement.classList.add("completed");
              tdElement.innerHTML = `✅ <br> <small>${tdElement.getAttribute(
                "data-mission-name"
              )}</small>`;
            }
          } else {
            alert("Erreur: " + data.error);
          }
        })
        .catch((error) =>
          console.error("Erreur lors de la soumission de la réponse :", error)
        );
    });
  }

  // Empêcher l'ouverture de la modale pour les missions verrouillées
  document.querySelectorAll(".puzzle-piece.locked").forEach((piece) => {
    piece.addEventListener("click", function (e) {
      e.preventDefault();
      return false;
    });
  });
});
