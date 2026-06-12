const db = require('./db');
const Solicitud = {
    create: async (data) => {
        const [result] = await db.query(
            'INSERT INTO solicitudes (nombre, email, telefono, servicio_id, archivo, mensaje) VALUES (?, ?, ?, ?, ?, ?)',
            [data.nombre, data.email, data.telefono, data.servicio_id, data.archivo || null, data.mensaje]
        );
        return result.insertId;
    },
    count: async () => {
        const [rows] = await db.query('SELECT COUNT(*) as total FROM solicitudes');
        return rows[0].total;
    },
    getMostRequested: async () => {
        const [rows] = await db.query(`
            SELECT sv.nombre, COUNT(*) as total 
            FROM solicitudes s JOIN servicios sv ON s.servicio_id = sv.id 
            GROUP BY s.servicio_id, sv.nombre ORDER BY total DESC LIMIT 1`);
        return rows[0] || null;
    },
    getLast: async (limit = 5) => {
        const [rows] = await db.query(`
            SELECT s.*, sv.nombre as servicio_nombre 
            FROM solicitudes s JOIN servicios sv ON s.servicio_id = sv.id 
            ORDER BY s.fecha DESC LIMIT ?`, [limit]);
        return rows;
    },
    countByStatus: async () => {
        const [rows] = await db.query('SELECT estado, COUNT(*) as total FROM solicitudes GROUP BY estado');
        return rows;
    },
    getByService: async () => {
        const [rows] = await db.query(`
            SELECT sv.nombre, COUNT(*) as total 
            FROM solicitudes s JOIN servicios sv ON s.servicio_id = sv.id 
            GROUP BY s.servicio_id, sv.nombre ORDER BY total DESC`);
        return rows;
    }
};
module.exports = Solicitud;
