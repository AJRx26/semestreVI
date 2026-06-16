const db = require('./db');

const Servicio = {

    getAll: async () => {
        const [rows] = await db.query('SELECT * FROM servicios ORDER BY id');
        return rows;
    },

    getAllWithCategoria: async () => {
        const [rows] = await db.query(`
            SELECT s.*, c.nombre AS categoria_nombre
            FROM servicios s
            LEFT JOIN categorias c ON s.categoria_id = c.id
            ORDER BY s.id
        `);
        return rows;
    },

    findById: async (id) => {
        //Evita inyeccion de SQL
        // Se usa ? como placeholders 
        const [rows] = await db.query('SELECT id FROM servicios WHERE id = ?', [id]);
        return rows[0] || null;
    },

    count: async () => {
        const [rows] = await db.query('SELECT COUNT(*) AS total FROM servicios');
        return rows[0].total;
    }

};

module.exports = Servicio;
