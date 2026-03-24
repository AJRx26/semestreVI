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