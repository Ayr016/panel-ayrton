function login(event) {
  event.preventDefault();

  const password = document.getElementById("password").value;
  const error = document.getElementById("error");

  // Cambiá esto por tu contraseña privada
  const claveCorrecta = "superclave2025";

  if (password === claveCorrecta) {
    window.location.href = "dashboard.html";
  } else {
    error.textContent = "Contraseña incorrecta";
  }
}
