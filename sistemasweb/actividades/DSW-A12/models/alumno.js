const pool = require('../data/datacontext')

const list = async function () {
	// el pool se inicializo en data/db.js
	// la conexion se cierra automaticamento cuando el query se resuelve
	const [rows, fields] = await pool.query(
		`SELECT alumno.id, alumno.nombre, alumno.promedio, materia.nombre AS materia_nombre 
			FROM materia INNER JOIN alumno ON materia.id=alumno.id_materia`);

	//regresa las filas
	return rows;
}

module.exports = { list }
