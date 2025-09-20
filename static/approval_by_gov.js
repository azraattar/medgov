document.addEventListener("DOMContentLoaded", function() {
  var supabaseClient = supabase.createClient(
    window.SUPABASE_CONFIG.url,
    window.SUPABASE_CONFIG.key
  );

  var doctorsGrid = document.getElementById("doctorsGrid");
  var toast = document.getElementById("toast");

  if (!toast) {
    console.error("Toast element not found");
    return;
  }

  toast.style.position = "fixed";
  toast.style.top = "20px";
  toast.style.right = "20px";
  toast.style.backgroundColor = "#333";
  toast.style.color = "white";
  toast.style.padding = "15px 20px";
  toast.style.borderRadius = "5px";
  toast.style.zIndex = "9999";
  toast.style.display = "none";
  toast.style.minWidth = "300px";

  function fetchPendingDoctors() {
    supabaseClient.from("doctors").select("*").then(function(result) {
      if (result.error) {
        console.error("Error fetching doctors:", result.error.message);
        showToast("Error fetching doctors: " + result.error.message);
        return;
      }

      var pendingDoctors = result.data.filter(function(doc) {
        return doc.status && doc.status.toLowerCase() === "pending";
      });

      renderDoctors(pendingDoctors);
    });
  }

  function renderDoctors(doctors) {
    doctorsGrid.innerHTML = "";

    if (doctors.length === 0) {
      doctorsGrid.innerHTML = "<p>No pending doctor requests found.</p>";
      return;
    }

    for (var i = 0; i < doctors.length; i++) {
      var doctor = doctors[i];
      var card = document.createElement("div");
      card.className = "doctor-card";

      var headerDiv = document.createElement("div");
      headerDiv.className = "doctor-header";

      var infoDiv = document.createElement("div");
      infoDiv.className = "doctor-info";

      var nameH3 = document.createElement("h3");
      nameH3.textContent = doctor.full_name;

      var specP = document.createElement("p");
      specP.className = "specialization";
      specP.textContent = doctor.specialization || "N/A";

      var statusSpan = document.createElement("span");
      statusSpan.className = "status-badge status-pending";
      statusSpan.textContent = doctor.status;

      infoDiv.appendChild(nameH3);
      infoDiv.appendChild(specP);
      infoDiv.appendChild(statusSpan);
      headerDiv.appendChild(infoDiv);

      var detailsDiv = document.createElement("div");
      detailsDiv.className = "doctor-details";

      var emailRow = document.createElement("div");
      emailRow.className = "detail-row";
      emailRow.innerHTML = "<span class='detail-label'>Email:</span> <span class='detail-value'>" + doctor.email + "</span>";

      var licenseRow = document.createElement("div");
      licenseRow.className = "detail-row";
      licenseRow.innerHTML = "<span class='detail-label'>License:</span> <span class='detail-value'>" + doctor.license_number + "</span>";

      detailsDiv.appendChild(emailRow);
      detailsDiv.appendChild(licenseRow);

      var buttonsDiv = document.createElement("div");
      buttonsDiv.className = "action-buttons";

      var approveBtn = document.createElement("button");
      approveBtn.className = "btn btn-approve";
      approveBtn.setAttribute("data-email", doctor.email);
      approveBtn.setAttribute("data-name", doctor.full_name);
      approveBtn.textContent = "Approve";

      approveBtn.addEventListener("click", function(e) {
        var btn = e.target;
        var email = btn.getAttribute("data-email");
        var name = btn.getAttribute("data-name");
        
        btn.disabled = true;
        btn.textContent = "Approving...";

        supabaseClient.from("doctors").update({
          status: "Approved",
          approved_at: new Date().toISOString()
        }).eq("email", email).select().then(function(updateResult) {
          if (updateResult.error) {
            console.error("Error:", updateResult.error);
            showToast("Failed to approve doctor");
            btn.disabled = false;
            btn.textContent = "Approve";
            return;
          }

          if (updateResult.data && updateResult.data.length > 0) {
            showToast("Doctor " + name + " approved successfully!");
            btn.closest(".doctor-card").remove();
            setTimeout(function() {
              fetchPendingDoctors();
            }, 1000);
          }
        });
      });

      buttonsDiv.appendChild(approveBtn);
      card.appendChild(headerDiv);
      card.appendChild(detailsDiv);
      card.appendChild(buttonsDiv);
      doctorsGrid.appendChild(card);
    }
  }

  function showToast(message) {
    if (!toast) {
      alert(message);
      return;
    }

    toast.textContent = message;
    toast.style.display = "block";

    if (message.includes("successfully")) {
      toast.style.backgroundColor = "#4CAF50";
    } else {
      toast.style.backgroundColor = "#f44336";
    }

    setTimeout(function() {
      toast.style.display = "none";
    }, 3000);
  }

  fetchPendingDoctors();
});
