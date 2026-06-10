const Solicitud = require('../models/solicitudModel');
const Servicio = require('../models/servicioModel');
const solicitudController = {
    postSolicitud: async (req, res, next) => {
        try {
            const { nombre, email, telefono, servicio_id, mensaje } = req.body;
            const errores = [];
            if (!nombre || nombre.trim().length < 3) errores.push('Nombre mínimo 3 caracteres.');
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errores.push('Email inválido.');
            if (!telefono || telefono.trim().length < 7) errores.push('Teléfono mínimo 7 caracteres.');
            if (!servicio_id || isNaN(servicio_id)) errores.push('Selecciona un servicio.');
            if (!mensaje || mensaje.trim().length < 10) errores.push('Mensaje mínimo 10 caracteres.');
            if (errores.length > 0) {
                const servicios = await Servicio.getAll();
                return res.render('index', { titulo: 'SeguriTech', servicios, errores, formData: req.body });
            }
            const archivo = req.file ? req.file.filename : null;
            const id = await Solicitud.create({
                nombre: nombre.trim(), email: email.trim(), telefono: telefono.trim(),
                servicio_id: parseInt(servicio_id), archivo, mensaje: mensaje.trim()
            });
            res.redirect('/?exito=true&id=' + id);
        } catch (e) { next(e); }
    },
    getDashboard: async (req, res, next) => {
        try { res.render('dashboard', { titulo: 'Dashboard' }); }
        catch (e) { next(e); }
    },
    getDashboardData: async (req, res, next) => {
        try {
            const [totalSolicitudes, servicioMasPedido, ultimasSolicitudes, estados, solicitudesPorServicio, totalServicios] = await Promise.all([
                Solicitud.count(), Solicitud.getMostRequested(), Solicitud.getLast(5),
                Solicitud.countByStatus(), Solicitud.getByService(), Servicio.count()
            ]);
            res.json({ success: true, data: { totalSolicitudes, totalServicios, servicioMasPedido: servicioMasPedido || { nombre: 'Sin datos', total: 0 }, ultimasSolicitudes, estados, solicitudesPorServicio } });
        } catch (e) { next(e); }
    }
};
module.exports = solicitudController;
