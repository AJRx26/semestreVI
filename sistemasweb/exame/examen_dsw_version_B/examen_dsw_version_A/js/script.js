// ==========================================
// EXAMEN PRÁCTICO - UVStream
// Completa las etapas solicitadas en el enunciado.
// ==========================================

const mensajeDinamico = document.getElementById("mensaje-dinamico");
const contenedorDinamico = document.getElementById("contenedor-dinamico");
const listaEstrenos = document.getElementById("lista-estrenos");
const panelEstadisticas = document.getElementById("panel-estadisticas");

const formulario = document.getElementById("formulario-suscripcion");
const campoNombre = document.getElementById("nombre");
const campoCorreo = document.getElementById("correo");
const campoPlan = document.getElementById("plan");
const inputArchivo = document.getElementById("archivo-comprobante");
const zonaArrastre = document.getElementById("zona-arrastre");
const archivoSeleccionado = document.getElementById("archivo-seleccionado");
const mensajeFormulario = document.getElementById("mensaje-formulario");
const salidaJson = document.getElementById("salida-json");

let archivoActual = null;

// --------------------------------------------------
// JavaScript y DOM
// Cambiar el mensaje al cargar la página
// Ejemplo esperado: "Plataforma cargada correctamente"
// --------------------------------------------------
// mensajeDinamico.textContent = "...";

// Crear dinámicamente un nuevo bloque dentro de #contenedor-dinamico

// Asociar eventos al botón #btn-eliminar-categoria
// Eliminar una tarjeta de categoría

// --------------------------------------------------
// JavaScript y DOM
// --------------------------------------------------

// 1. Mensaje dinamico al cargar
mensajeDinamico.textContent = "Plataforma cargada correctamente";

// 2. Crear boton para eliminar categorias
const btnEliminar = document.createElement("button");
btnEliminar.id = "btn-eliminar-categoria";
btnEliminar.textContent = "Eliminar categoria";
contenedorDinamico.appendChild(btnEliminar);

// Eliminar categorias una por una
btnEliminar.addEventListener("click", () => {
  const categorias = document.querySelectorAll(".tarjeta-categoria");
  if (categorias.length > 0) {
    categorias[0].remove();
  } else {
    mensajeDinamico.textContent = "Sin categorias que eliminar";
  }
});

// 3. Crear sección dinamica
const nuevaSeccion = document.createElement("section");
const titulo = document.createElement("h3");

titulo.textContent = "Seccion dinamica - xd";

const contenido = document.createElement("p");
contenido.textContent = "Esta parte fue generada dinamicamente desde JavaScript.";
nuevaSeccion.appendChild(titulo);
nuevaSeccion.appendChild(contenido);
contenedorDinamico.appendChild(nuevaSeccion);

// --------------------------------------------------
// Formulario + comprobante de pago
// --------------------------------------------------
const mostrarArchivo = (archivo) => {
  archivoSeleccionado.textContent = "Archivo seleccionado: " + archivo.name;
  archivoSeleccionado.style.color = "#18529D";
};

zonaArrastre.addEventListener("click", () => {
  inputArchivo.click();
});

zonaArrastre.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    inputArchivo.click();
  }
});

inputArchivo.addEventListener("change", () => {
  // TODO: manejar selección de archivo y usar try/catch
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

zonaArrastre.addEventListener("dragover", (event) => {
  event.preventDefault();
  zonaArrastre.classList.add("activa");
});

zonaArrastre.addEventListener("dragleave", () => {
  zonaArrastre.classList.remove("activa");
});

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

formulario.addEventListener("reset", () => {
  archivoActual = null;
  archivoSeleccionado.textContent = "Ningún archivo seleccionado.";
  archivoSeleccionado.style.color = "";
  mensajeFormulario.textContent = "";
  salidaJson.textContent = "";
});

formulario.addEventListener("submit", (event) => {
  event.preventDefault();

  // Validar:
  // 1. nombre no vacío
  // 2. correo válido
  // 3. selección obligatoria
  // 4. archivo obligatorio
  // 5. mostrar errores en rojo y éxito en verde

  //Construir un objeto JS y convertirlo con JSON.stringify()
  //Mostrar el resultado en #salida-json

  if (campoNombre.value.trim() === "") {
    mensajeFormulario.textContent = "El nombre completo es obligatorio.";
    mensajeFormulario.style.color = "red";
    campoNombre.focus();
    return;
  }

  if (!campoCorreo.value.includes("@")) {
    mensajeFormulario.textContent = "El correo no es válido.";
    mensajeFormulario.style.color = "red";
    campoCorreo.focus();
    return;
  }

  if (campoPlan.value === "") {
    mensajeFormulario.textContent = "Debes seleccionar un plan.";
    mensajeFormulario.style.color = "red";
    campoPlan.focus();
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

// --------------------------------------------------
// AJAX + JSON
// --------------------------------------------------
const cargarEstrenos = () => {
  // Usar fetch("datos/estrenos.json")
  // Insertar tarjetas o artículos en #lista-estrenos
  // Usar .catch(...)
  fetch("datos/estrenos.json")
  .then(respuesta => respuesta.json())
  .then(estrenos => {
    listaEstrenos.innerHTML = "";

    estrenos.forEach(estreno => {
      const bloque = document.createElement("article");

      bloque.innerHTML = `
        <h3>${estreno.titulo} (${estreno.anio})</h3>
        <p>Categoría: ${estreno.categoria}</p>
        <p>${estreno.descripcion}</p>
      `;

      listaEstrenos.appendChild(bloque);
    });
  })
  .catch(error => {
    console.error("Error al cargar estrenos:", error);
  });
};

const cargarEstadisticas = () => {
  //Usar fetch("datos/estadisticas.json")
  //Insertar tarjetas en #panel-estadisticas
  //Usar .catch(...)
  fetch("datos/estadisticas.json")
  .then(respuesta => respuesta.json())
  .then(indicadores => {
    panelEstadisticas.innerHTML = "";

    indicadores.forEach(indicador => {
      const bloque = document.createElement("div");
      bloque.classList.add("tarjeta-estadistica");

      bloque.innerHTML = `
        <h3>${indicador.nombre}</h3>
        <p>${indicador.valor}</p>
      `;

      panelEstadisticas.appendChild(bloque);
    });
  })
  .catch(error => {
    console.error("Error al cargar estadísticas:", error);
  });
};

//Llamar a cargarEstrenos() y cargarEstadisticas()
cargarEstrenos()
cargarEstadisticas()

//Convertir datos del formulario a JSON
document.getElementById("formulario-suscripcion").addEventListener("submit", function (event) {
  event.preventDefault();

  const datos = {
    nombre: document.getElementById("nombre").value,
    correo: document.getElementById("correo").value,
    plan: document.getElementById("plan").value
  };

  /*Convierte el objeto javascript "solicitud" en una cadena JSON estableciendo el parametro replacer=null y el parametro space=2*/
  const datosJSON = JSON.stringify(datos, null, 2);
  salidaJson.textContent = datosJSON;
});