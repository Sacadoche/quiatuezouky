document.addEventListener("DOMContentLoaded", function () {
  const missionModal = document.getElementById("missionModal");
  const submitResponseButton = document.getElementById("submit-response");
  const responseField = document.getElementById("mission-response");
  const hiddenMissionIdField = document.getElementById("hidden-mission-id");
  const validatedMessage = document.getElementById("mission-validated-message");

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
        console.error("Élément #mission-id introuvable dans la modale.");
      }

      fetch(`/get_mission_info/${missionId}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Erreur réseau");
          }
          return response.json();
        })
        .then((data) => {
          if (data.success) {
            const modalTitle = missionModal.querySelector(".modal-title");
            modalTitle.textContent = `Mission ${missionId}`;
            modalBody.querySelector("#mission-name").textContent =
              data.mission.name;
            modalBody.querySelector("#mission-description").textContent =
              data.mission.description || "Aucune description";
            modalBody.querySelector("#mission-status").textContent =
              data.mission.status;

            // Pièce jointe
            const attachBox = modalBody.querySelector("#mission-attachment");
            const openLink = modalBody.querySelector(
              "#mission-attachment-open"
            );
            const dlLink = modalBody.querySelector(
              "#mission-attachment-download"
            );
            if (data.mission.attachment_url) {
              attachBox.style.display = "block";
              openLink.href = data.mission.attachment_url;
              dlLink.href = data.mission.attachment_url;
            } else {
              attachBox.style.display = "none";
              openLink.removeAttribute("href");
              dlLink.removeAttribute("href");
            }
          } else {
            console.error("Erreur:", data.error);
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
