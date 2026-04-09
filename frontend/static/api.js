// api.js
// Auto-intercepts all form submissions and sends to Flask backend

const API_BASE_URL = "http://localhost:3000";

document.addEventListener("DOMContentLoaded", () => {
  // Find all forms on the page
  const forms = document.querySelectorAll("form");

  forms.forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault(); // Stop normal HTML submission

      // The action attribute tells us where the form wanted to go
      let endpoint = form.getAttribute("action") || "";

      // If the monolithic app used action="#" it means "post to the current URL"
      if (endpoint === "#" || endpoint === "") {
        let currentPath = window.location.pathname; // Ex: "/login_user.html"
        // Strip the .html to match the Flask endpoint signature
        endpoint = currentPath.replace(".html", "");
        if (endpoint === "") endpoint = "/";
      } else if (endpoint.startsWith("http")) {
        const url = new URL(endpoint);
        endpoint = url.pathname;
      }

      const formData = new FormData(form);

      try {
        // Post data to the Python API
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        console.log("Backend Response:", data);

        // Route handling logic
        if (data.redirect) {
          let redir = data.redirect;
          if (redir === "/") redir = "index.html";
          else if (redir.startsWith("/")) redir = redir.substring(1) + ".html";
          window.location.href = redir;
        } else if (data.template) {
          window.location.href = data.template;
        } else {
          // Refresh or alert if no explicit redirect
          alert("Success!");
        }
      } catch (error) {
        console.error("Error communicating with backend:", error);
        alert("Failed to connect to backend server.");
      }
    });
  });
});
