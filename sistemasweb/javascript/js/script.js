import { calcularPrecioConImpuesto } from "./utilidades.js";

console.log("JavaScript esta funcionando");

let nombreJuego = "Legend of Adventure";
let precio = 40;
let disponible = true;
let precioJuego = 60;
let nombre = 'visitante';
let juego = "Legend of Adventura";
let mensaje = "El videojuego seleccionado es: " + juego;
let mensaje2 = `El videojuego seleccionado es: ${juego}`;
let precioFinal = calcularPrecioConImpuesto(60);
let juegos = ["Zelda", "Mario Kart", "FIFA", "Halo"];
let categoria = "accion";

console.log(nombreJuego);
console.log(precio);
console.log(disponible);
console.log('Hola ' + nombre + ', bienvenido al sitio.');
console.log('Hola "visitante", bienvenido al sitio.')
console.log("Hola " + nombre + ", bienvenido al sitio.")
console.log(`Hola ${nombre}, bienvenido al sitio.`)
console.log(mensaje);
console.log(mensaje2);
console.log(precioFinal);
console.log(juegos);
console.log(juegos[0]);

juegos.push("Minecraft");
console.log(juegos)

if(precioJuego < 50){
    console.log("Oferta disponible");
}else{
    console.log("Precio normal");
}

function comprarJuego() {
    document.getElementById("info").textContent = "Has agregado el juego al carrito";
}

document.getElementById("btnComprar").addEventListener("click", comprarJuego);

switch(categoria){
    case "accion":
        console.log("Juegos accion");
        break;

    case "deportes":
        console.log("Juegos deportivos");
        break;

    default:
        console.log("Categoria no encontrada");
}

juego = {
    nombre: "Zelda",
    precio: 60,
    disponible: true
};

console.log(juego.nombre);
console.log(juego.precio);

document.getElementById("info").textContent = `Juego: ${juego.nombre} - Precio: $${juego.precio}`;

const myJSON = '{"name": "John", "age": 30, "car": null}';
const myObj = JSON.parse(myJSON);
//x contiene John
let x = myObj.name;
console.log(myObj);

let text = "";
for (const x in myObj) {
    text += x + ":" + myObj[x] + ", ";
}
//Escribe las propiedades y su valor
console.log(text);

/*
const xhr = new XMLHttpRequest();
xhr.open("GET", "datos/videojuegos.json");

xhr.addEventListener("load", function () {
    const videojuegos = JSON.parse(xhr.responseText);
    const listaJuegos = document.getElementById("lista-juegos");

    videojuegos.forEach((juego) => {
        const tarjeta = document.createElement("article");
        tarjeta.classList.add("juego");

        tarjeta.innerHTML = `
            <h3>${juego.nombre}</h3>
            <p>Precio: $${juego.precio}</p>
            <p>Categoria: ${juego.categoria}</p>
            <button type="button">Comprar</button>
        `;
        listaJuegos.appendChild(tarjeta);
    });
});
xhr.send();
*/

fetch("datos/videojuegos.json")
  .then(respuesta => respuesta.json())
  .then(videojuegos => {
    const listaJuegos = document.getElementById("lista-juegos");

    videojuegos.forEach((juego) => {
      const tarjeta = document.createElement("article");
      tarjeta.classList.add("juego");
      tarjeta.innerHTML = `
        <h3>${juego.nombre}</h3>
        <p>Precio: $${juego.precio}</p>
        <p>Categoría: ${juego.categoria}</p>
        <button type="button">Comprar</button>
      `;
      listaJuegos.appendChild(tarjeta);
    })
  })
  .catch(error => {
    document.getElementById("info").textContent = "Error al cargar los datos";
  });

/*
fetch("datos/videojuegos.json")
  .then(respuesta => respuesta.json())
  .then(videojuegos1 => {
    const info = document.getElementById("info");
    info.textContent = `Se cargaron ${videojuegos1.length} videojuegos`;
  })
  .catch(error => {
    document.getElementById("info").textContent = "Error al cargar los datos";
  });
*/