const db = require('./db');
const Servicio = {
    getAll: async () => {
        const [rows] = await db.query('SELECT * FROM servicios ORDER BY id');
        return rows;
    },
    getAllWithCategoria: async () => {
        const [rows] = await db.query(`
            SELECT s.*, c.nombre as categoria_nombre 
            FROM servicios s LEFT JOIN categorias c ON s.categoria_id = c.id 
            ORDER BY s.id`);
        return rows;
    },
    count: async () => {
        const [rows] = await db.query('SELECT COUNT(*) as total FROM servicios');
        return rows[0].total;
    }
};
module.exports = Servicio;
