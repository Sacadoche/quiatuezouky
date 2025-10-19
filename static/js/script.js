document.addEventListener("DOMContentLoaded", function () {
  // Gestion de la modale
  const missionModal = document.getElementById("missionModal");
  if (missionModal) {
    missionModal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      const missionId = button.getAttribute("data-mission-id");
      console.log(`/get_mission_info/${missionId}`);
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
            const modalBody = missionModal.querySelector(".modal-body");

            modalTitle.textContent = `Mission ${missionId}`;
            modalBody.querySelector("#mission-id").textContent = missionId;
            modalBody.querySelector("#mission-name").textContent =
              data.mission.name;
            modalBody.querySelector("#mission-description").textContent =
              data.mission.description || "Aucune description";
            modalBody.querySelector("#mission-status").textContent =
              data.mission.status;
          } else {
            console.error("Erreur:", data.error);
            const modalBody = missionModal.querySelector(".modal-body");
            modalBody.querySelector("#mission-id").textContent = missionId;
            modalBody.querySelector(
              "#mission-name"
            ).textContent = `Mission ${missionId}`;
            modalBody.querySelector("#mission-description").textContent =
              "Erreur de chargement des données";
            modalBody.querySelector("#mission-status").textContent = "Inconnu";
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          const modalBody = missionModal.querySelector(".modal-body");
          modalBody.querySelector("#mission-id").textContent = missionId;
          modalBody.querySelector(
            "#mission-name"
          ).textContent = `Mission ${missionId}`;
          modalBody.querySelector("#mission-description").textContent =
            "Erreur de connexion au serveur";
          modalBody.querySelector("#mission-status").textContent = "Inconnu";
        });
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
