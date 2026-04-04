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

