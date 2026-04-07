const mensajeDinamico = document.getElementById("mensaje-dinamico");
mensajeDinamico.textContent = "Portal cargado correctamente. JavaScript se encuentra activo.";

mensajeDinamico.style.backgroundColor = "#e8f5e9";
mensajeDinamico.style.color = "#18529D";
mensajeDinamico.style.padding = "12px";
mensajeDinamico.style.borderLeft = "5px solid #28AD56";
mensajeDinamico.style.fontWeight = "bold";

//Cambiar atributo de Contacto de menu de navegación

const enlaceContacto = document.querySelector('nav a[href="#contacto"]');
enlaceContacto.setAttribute("title", "Ir a la sección de contacto y reporte de incidente");

// Sección acciones rapidas
const accionesRapidas = document.createElement("section");
accionesRapidas.id = "acciones-rapidas";
accionesRapidas.innerHTML = `
  <h2>Acciones rapidas</h2>
  <p>Utiliza los siguientes botones para interactuar con el portal.</p>
  <button type="button" id="btn-resaltar-avisos">Resaltar avisos</button>
  <button type="button" id="btn-ocultar-primer-aviso">Eliminar primer aviso</button>
  <button type="button" id="btn-restaurar-mensaje">Restaurar mensaje</button>
  `;

// Insertar la sección "Acciones rapidas" en el documento
const seccionServicios = document.getElementById("servicios");
seccionServicios.insertAdjacentElement("beforebegin", accionesRapidas);

// Eventos de "Acciones rapidas"
document.getElementById("btn-resaltar-avisos").addEventListener("click", function() {
    const avisos = document.querySelectorAll(".aviso");

    avisos.forEach(function (aviso) {
        aviso.style.backgroundColor = "#fff8e1";
        aviso.style.borderLeft = "6px solid #f9a825";
    });
});

document.getElementById("btn-restaurar-mensaje").addEventListener("click", function() {
    mensajeDinamico.textContent = "Bienvenidos al Portal Institucional del Centro de Computo.";
    mensajeDinamico.style.backgroundColor = "#e8f5e9";
    mensajeDinamico.style.color = "#18529D";
});

document.getElementById("btn-ocultar-primer-aviso").addEventListener("click", function () {
    const primerAviso = document.querySelector(".aviso");

    if (primerAviso) {
        primerAviso.remove();
        mensajeDinamico.textContent = "El primer aviso fue eliminado correctamente.";
    }
    else {
        mensajeDinamico.textContent = "Ya no existen avisos para eliminar.";
    }
});

//Carrusel
const imagenesCarrusel = [
  {
    src:"img/centro-computo-1.jpg",
    alt:"Vista general del laboratorio de cómputo",
    descripcion:"Vista general del laboratorio."
  },
  {
    src:"img/centro-computo-2.jpg",
    alt:"Equipo de cómputo en el Centro de Cómputo",
    descripcion:"Equipos disponibles para actividades académicas."
  },
  {
    src:"img/centro-computo-3.jpg",
    alt:"Área de trabajo del Centro de Cómputo",
    descripcion:"Espacios de trabajo para estudiantes y personal."
  }
];

let indiceActual = 0;

const imagenCarrusel = document.getElementById("imagen-carrusel");
const descripcionCarrusel = document.getElementById("descripcion-carrusel");

function mostrarImagen(indice) {
  imagenCarrusel.src = imagenesCarrusel[indice].src;
  imagenCarrusel.alt = imagenesCarrusel[indice].alt;
  descripcionCarrusel.textContent = imagenesCarrusel[indice].descripcion;
}

document.getElementById("btn-siguiente").addEventListener("click", function () {
  indiceActual++;
  if (indiceActual >= imagenesCarrusel.length) {
    indiceActual = 0;
  }
  mostrarImagen(indiceActual);
});

document.getElementById("btn-anterior").addEventListener("click", function () {
  indiceActual--;
  if (indiceActual < 0) {
    indiceActual = imagenesCarrusel.length - 1;
  }
  mostrarImagen(indiceActual);
});

//mouseover mouseout sobre enlaces de menú
const enlacesMenu = document.querySelectorAll("nav a");

enlacesMenu.forEach((enlace) => {
  enlace.addEventListener("mouseover", () => {
    enlace.style.transform = "scale(1.05)";
  });

  enlace.addEventListener("mouseout", () => {
    enlace.style.transform = "scale(1)";
  });
});

//Zona Drag and Drop para carga de archivos evidencia
const formulario = document.querySelector("form");
const campoNombre = document.getElementById("nombre");
const campoCorreo = document.getElementById("correo");
const campoRol = document.getElementById("rol");
const campoTipo = document.getElementById("tipo");
const campoDescripcion = document.getElementById("descripcion");
const inputArchivo = document.getElementById("archivo-evidencia");
const zonaArrastre = document.getElementById("zona-arrastre");
const archivoSeleccionado = document.getElementById("archivo-seleccionado");
const mensajeFormulario = document.getElementById("mensaje-formulario");

/* Variable para conservar el archivo actual, ya sea seleccionado o arrastrado */
let archivoActual = null;

/* Función para mostrar el nombre del archivo seleccionado */
const mostrarArchivo = (archivo) => {
  archivoSeleccionado.textContent = "Archivo seleccionado: " + archivo.name;
  archivoSeleccionado.style.color = "#18529D";
};

/* Abrir selector de archivos al hacer clic */
zonaArrastre.addEventListener("click", () => {
  inputArchivo.click();
});

/* También permitir activarlo con teclado */
zonaArrastre.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    inputArchivo.click();
  }
});

/* Cuando se selecciona un archivo desde el explorador */
inputArchivo.addEventListener("change", () => {
  try {
    if (inputArchivo.files.length === 0) {
      throw new Error("No se seleccionó ningún archivo.");
    }
    archivoActual = inputArchivo.files[0];
    mostrarArchivo(archivoActual);
  } catch (error) {
    archivoActual = null;
    archivoSeleccionado.textContent = "Error: " + error.message;
    archivoSeleccionado.style.color = "red";
  }
});

/* Permitir arrastrar archivo sobre la zona */
zonaArrastre.addEventListener("dragover", (event) => {
  event.preventDefault();
  zonaArrastre.classList.add("activa");
});

/* Quitar estilo visual al salir de la zona */
zonaArrastre.addEventListener("dragleave", () => {
  zonaArrastre.classList.remove("activa");
});

/* Soltar archivo en la zona */
zonaArrastre.addEventListener("drop", (event) => {
  event.preventDefault();
  zonaArrastre.classList.remove("activa");
  try {
    const archivos = event.dataTransfer.files;
    if (archivos.length === 0) {
      throw new Error("No se arrastró ningún archivo.");
    }
    archivoActual = archivos[0];
    mostrarArchivo(archivoActual);
  } catch (error) {
    archivoActual = null;
    archivoSeleccionado.textContent = "Error: " + error.message;
    archivoSeleccionado.style.color = "red";
  }
});

/* Limpiar mensaje visual al reiniciar el formulario */
formulario.addEventListener("reset", () => {
  archivoActual = null;
  archivoSeleccionado.textContent = "Ningún archivo seleccionado.";
  archivoSeleccionado.style.color = "";
  mensajeFormulario.textContent = "";
});

//Validación de formulario
formulario.addEventListener("submit", function (event) {
  event.preventDefault();

  if (campoNombre.value.trim() === "") {
    mensajeFormulario.textContent = "El nombre completo es obligatorio.";
    mensajeFormulario.style.color = "red";
    campoNombre.focus();
    return;
  }

  if (!campoCorreo.value.includes("@")) {
    mensajeFormulario.textContent = "El correo institucional no es válido.";
    mensajeFormulario.style.color = "red";
    campoCorreo.focus();
    return;
  }

  if (campoRol.value === "") {
    mensajeFormulario.textContent = "Debes seleccionar un rol.";
    mensajeFormulario.style.color = "red";
    campoRol.focus();
    return;
  }

  if (campoTipo.value === "") {
    mensajeFormulario.textContent = "Debes seleccionar un tipo de solicitud.";
    mensajeFormulario.style.color = "red";
    campoTipo.focus();
    return;
  }

  if (campoDescripcion.value.trim().length < 10) {
    mensajeFormulario.textContent = "La descripción debe contener al menos 10 caracteres.";
    mensajeFormulario.style.color = "red";
    campoDescripcion.focus();
    return;
  }

  if (!archivoActual) {
    mensajeFormulario.textContent = "Debes adjuntar un archivo de evidencia.";
    mensajeFormulario.style.color = "red";
    zonaArrastre.focus();
    return;
  }
  mensajeFormulario.textContent = "Formulario validado correctamente. Datos listos para enviarse.";
  mensajeFormulario.style.color = "green";
});

const btnModo = document.createElement("button");
btnModo.type = "button";
btnModo.id = "btn-modo";
btnModo.textContent = "Activar modo nocturno";

document.querySelector("header").insertAdjacentElement("beforeend", btnModo);

btnModo.addEventListener("click", function () {
  document.body.classList.toggle("modo-nocturno");
  if (document.body.classList.contains("modo-nocturno")) {
    btnModo.textContent = "Desactivar modo nocturno";
  } else {
    btnModo.textContent = "Activar modo nocturno";
  }
});
