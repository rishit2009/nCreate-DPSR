const navMenu = document.getElementById("nav-menu");
const navToggle = document.getElementById("nav-toggle");
const navClose = document.getElementById("nav-close");

navClose.style.display = 'none'; // Initially hide close button

// Function to close the nav
navClose.addEventListener("click", () => {
   navMenu.classList.add("closed");
   navClose.style.display = "none"; // Hide close button
   navToggle.style.display = "block"; // Show toggle button
});

// Function to open the nav
navToggle.addEventListener("click", () => {
   navMenu.classList.remove("closed");
   navClose.style.display = "block"; // Show close button
   navToggle.style.display = "none"; // Hide toggle button
});


