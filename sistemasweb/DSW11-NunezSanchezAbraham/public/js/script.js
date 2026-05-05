//Función reutilizable para cargar avisos
const cargarAvisos = () => {
    const mensajeDinamico2 = document.getElementById("mensaje-dinamico");
    mensajeDinamico2.textContent = "Cargando avisos del portal...";

    fetch("datos/avisos.json")
    .then(respuesta => respuesta.json())
    .then(avisos => {
        const listaAvisos = document.getElementById("lista-avisos");
        //Limpiar contenido previo (IMPORTANTE)
        listaAvisos.innerHTML = "";

        avisos.forEach(aviso => {
            const tarjetaAviso = document.createElement("article");
            tarjetaAviso.classList.add("aviso");
            tarjetaAviso.innerHTML = `
            <h3>${aviso.titulo}</h3>
            <p><strong>Fecha:</strong> ${aviso.fecha}</p>
            <p>${aviso.descripcion}</p>
            `;
            listaAvisos.appendChild(tarjetaAviso);
        });
        mensajeDinamico2.textContent = `Se cargaron ${avisos.length} avisos correctamente.`;
    })

    .catch(error => {
        mensajeDinamico2.textContent = "Error al cargar los avisos del portal.";
        console.log("Ocurrió un error:", error);

    });
};

//Llamada a la función cargarAvisos, para que se carguen desde el inicio
cargarAvisos();


const mensajeDinamico = document.getElementById("mensaje-dinamico");
const enlaceContacto = document.querySelector('nav a[href="#contacto"]');
const seccionServicios = document.getElementById("servicios");
const enlacesMenu = document.querySelectorAll("nav a");

// Elementos del Formulario
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

// Elementos del Carrusel
const imagenCarrusel = document.getElementById("imagen-carrusel");
const descripcionCarrusel = document.getElementById("descripcion-carrusel");

mensajeDinamico.textContent = "Cargando información del portal...";
mensajeDinamico.style.backgroundColor = "#e8f5e9";
mensajeDinamico.style.color = "#18529D";
mensajeDinamico.style.padding = "12px";
mensajeDinamico.style.borderLeft = "5px solid #28AD56";
mensajeDinamico.style.fontWeight = "bold";

enlaceContacto.setAttribute("title", "Ir a la sección de contacto y reporte de incidente");

// Creación de sección Acciones Rápidas
const accionesRapidas = document.createElement("section");
accionesRapidas.id = "acciones-rápidas";
accionesRapidas.innerHTML = `
    <h2>Acciones rápidas</h2>
    <p>Utiliza los siguientes botones para interactuar con el portal.</p>
    <button type="button" id="btn-resaltar-avisos">Resaltar avisos</button>
    <button type="button" id="btn-ocultar-primer-aviso">Eliminar primer aviso</button>
    <button type="button" id="btn-cargar-avisos">Cargar avisos</button>
    <button type="button" id="btn-restaurar-mensaje">Restaurar mensaje</button>
`;
seccionServicios.insertAdjacentElement("beforebegin", accionesRapidas);
document.getElementById("btn-cargar-avisos").addEventListener("click", cargarAvisos);

// Creación de botón Modo Nocturno
const btnModo = document.createElement("button");
btnModo.type = "button";
btnModo.id = "btn-modo";
btnModo.textContent = "Activar modo nocturno";
document.querySelector("header").insertAdjacentElement("beforeend", btnModo);

// Creación de carrusel

const imagenesCarrusel = [
    {
        src: "img/portal-institucional.jpg",
        alt: "Vista general del laboratorio de cómputo",
        descripcion: "Vista general del laboratorio."
    },
    {
        src: "img/centro-computo-2.jpg",
        alt: "Equipo de cómputo en el Centro de Cómputo",
        descripcion: "Equipos disponibles para actividades académicas."
    },
    {
        src: "img/centro-computo-3.jpg",
        alt: "Área de trabajo del Centro de Cómputo",
        descripcion: "Espacios de trabajo para estudiantes y personal"
    }
];

let indiceActual = 0;

function mostrarImagen(indice){
    imagenCarrusel.src = imagenesCarrusel[indice].src;
    imagenCarrusel.alt = imagenesCarrusel[indice].alt;
    descripcionCarrusel.textContent = imagenesCarrusel[indice].descripcion;
}

// Eventos Acciones Rápidas
document.getElementById("btn-resaltar-avisos").addEventListener("click", function () {
    const avisos = document.querySelectorAll(".aviso");
    avisos.forEach(function (aviso) {
        aviso.style.backgroundColor = "#fff8e1";
        aviso.style.borderLeft = "6px solid #f9a825";
    });
});

document.getElementById("btn-restaurar-mensaje").addEventListener("click", function () {
    mensajeDinamico.textContent = "Bienvenido al Portal Institucional del Centro de Cómputo.";
    mensajeDinamico.style.backgroundColor = "#e8f5e9";
    mensajeDinamico.style.color = "#18529D";
});

document.getElementById("btn-ocultar-primer-aviso").addEventListener("click", function () {
    const primerAviso = document.querySelector(".aviso");
    if (primerAviso) {
        primerAviso.remove();
        mensajeDinamico.textContent = "El primer aviso fue eliminado correctamente.";
    } else {
        mensajeDinamico.textContent = "Ya no existen avisos para eliminar.";
    }
});

// Eventos Navegación Carrusel
document.getElementById("btn-siguiente").addEventListener("click", function() {
    indiceActual++;
    if (indiceActual >= imagenesCarrusel.length) indiceActual = 0;
    mostrarImagen(indiceActual);
});

document.getElementById("btn-anterior").addEventListener("click", function() {
    indiceActual--;
    if (indiceActual < 0) indiceActual = imagenesCarrusel.length - 1;
    mostrarImagen(indiceActual);
});

// Efectos de Menú
enlacesMenu.forEach((enlace) => {
    enlace.addEventListener("mouseover", () => enlace.style.transform = "scale(1.05)");
    enlace.addEventListener("mouseout", () => enlace.style.transform = "scale(1)");
});

// Evento Modo Nocturno
btnModo.addEventListener("click", function () {
    document.body.classList.toggle("modo-nocturno");
    btnModo.textContent = document.body.classList.contains("modo-nocturno") 
        ? "Desactivar modo nocturno" 
        : "Activar modo nocturno";
});


// Carga de archivos

let archivoActual = null;

const mostrarArchivo = (archivo) => {
    archivoSeleccionado.textContent = "Archivo seleccionado: " + archivo.name;
    archivoSeleccionado.style.color = "#18529D";
};

zonaArrastre.addEventListener("click", () => inputArchivo.click());

zonaArrastre.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        inputArchivo.click();
    }
});

inputArchivo.addEventListener("change", () => {
    try {
        if (inputArchivo.files.length === 0) throw new Error("No se seleccionó ningún archivo.");
        archivoActual = inputArchivo.files[0];
        mostrarArchivo(archivoActual);
    } catch (error) {
        archivoActual = null;
        archivoSeleccionado.textContent = "Error: " + error.message;
        archivoSeleccionado.style.color = "red";
    }
});

zonaArrastre.addEventListener("dragover", (event) => {
    event.preventDefault();
    zonaArrastre.classList.add("activa");
});

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
        // Asignar el archivo al input para que el formulario lo envíe realmente al backend
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(archivoActual);
        inputArchivo.files = dataTransfer.files;

        mostrarArchivo(archivoActual);
    } catch (error) {
        archivoActual = null;
        archivoSeleccionado.textContent = "Error: " + error.message;
        archivoSeleccionado.style.color = "red";
    }
});


//Envío de formulario
const formularioContacto = document.getElementById("formulario-contacto");

if (formularioContacto) {
    formularioContacto.addEventListener("submit", function (event) {

        const solicitud = {

            nombre: document.getElementById("nombre").value,

            correo: document.getElementById("correo").value,

            rol: document.getElementById("rol").value,

            tipo: document.getElementById("tipo").value,

            descripcion: document.getElementById("descripcion").value

        };

        const solicitudJSON = JSON.stringify(solicitud, null, 2);
        const salidaJSON = document.getElementById("salida-json");

        if (salidaJSON) {
            salidaJSON.textContent = solicitudJSON;
        }

        if (campoNombre.value.trim() === "") {
            event.preventDefault();
            mensajeFormulario.textContent = "El nombre completo es obligatorio.";
            mensajeFormulario.style.color = "red";
            campoNombre.focus();
            return;
        }

        if (!campoCorreo.value.includes("@")) {
            event.preventDefault();
            mensajeFormulario.textContent = "El correo institucional no es válido.";
            mensajeFormulario.style.color = "red";
            campoCorreo.focus();
            return;
        }

        if (campoRol.value === "") {
            event.preventDefault();
            mensajeFormulario.textContent = "Debes seleccionar un rol.";
            mensajeFormulario.style.color = "red";
            campoRol.focus();
            return;
        }

        if (campoTipo.value === "") {
            event.preventDefault();
            mensajeFormulario.textContent = "Debes seleccionar un tipo de solicitud.";
            mensajeFormulario.style.color = "red";
            campoTipo.focus();
            return;
        }

        if (campoDescripcion.value.trim().length < 10) {
            event.preventDefault();
            mensajeFormulario.textContent = "La descripción debe contener al menos 10 caracteres.";
            mensajeFormulario.style.color = "red";
            campoDescripcion.focus();
            return;
        }            

        if (!archivoActual) {
            event.preventDefault();
            mensajeFormulario.textContent = "Debes adjuntar un archivo de evidencia.";
            mensajeFormulario.style.color = "red";
            zonaArrastre.focus();
            return;
        }

        mensajeFormulario.textContent = "Formulario validado correctamente. Enviando datos...";
        mensajeFormulario.style.color = "green";
    });
}



//JSON
//Carga de indicadores con fetch()
fetch("datos/indicadores.json")
.then(respuesta => respuesta.json())
.then(indicadores => {
    const panelIndicadores = document.getElementById("panel-indicadores");

    indicadores.forEach(indicador => {
        const bloque = document.createElement("article");
        bloque.classList.add("tarjeta-indicador");
        bloque.innerHTML = `
            <h3>${indicador.nombre}</h3>
            <p>${indicador.valor}</p>
        `;

        panelIndicadores.appendChild(bloque);
    });
})

.catch(error => {
    console.log("Error al cargar indicadores:", error);
})

