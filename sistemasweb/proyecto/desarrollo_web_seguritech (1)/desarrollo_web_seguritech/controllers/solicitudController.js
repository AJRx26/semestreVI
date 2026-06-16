const validator = require('validator');
const Solicitud = require('../models/solicitudModel');
const Servicio = require('../models/servicioModel');

const solicitudController = {

    postSolicitud: async (req, res, next) => {
        const isAjax = req.headers['x-requested-with'] === 'XMLHttpRequest';

        try {
            // --- Sanitización de entradas ---
            const nombre     = validator.escape(validator.trim(req.body.nombre     || ''));
            const email      = validator.trim(req.body.email      || '').toLowerCase();
            const telefono   = validator.trim(req.body.telefono   || '');
            const servicio_id = validator.trim(String(req.body.servicio_id || ''));
            const mensaje    = validator.escape(validator.trim(req.body.mensaje    || ''));

            const errores = [];

            // --- Validaciones ---
            if (nombre.length < 3 || nombre.length > 150) {
                errores.push('Nombre debe tener entre 3 y 150 caracteres.');
            }

            if (!validator.isEmail(email)) {
                errores.push('Email inválido.');
            }

            // Solo dígitos, espacios, guiones y paréntesis; mínimo 7 dígitos
            if (!telefono || !/^[\d\s\-()+]{7,20}$/.test(telefono)) {
                errores.push('Teléfono inválido (mínimo 7 dígitos).');
            }

            if (!servicio_id || !validator.isInt(servicio_id, { min: 1 })) {
                errores.push('Selecciona un servicio válido.');
            } else {
                // Verificar que el servicio exista realmente en la BD
                const servicioValido = await Servicio.findById(parseInt(servicio_id));
                if (!servicioValido) {
                    errores.push('El servicio seleccionado no existe.');
                }
            }

            if (mensaje.length < 10 || mensaje.length > 2000) {
                errores.push('Mensaje debe tener entre 10 y 2000 caracteres.');
            }

            // --- Si hay errores, devolver al formulario ---
            if (errores.length > 0) {
                if (isAjax) {
                    return res.status(400).json({ success: false, errores });
                }

                const servicios = await Servicio.getAllWithCategoria();
                return res.render('contacto', {
                    titulo: 'Contacto',
                    servicios,
                    errores,
                    // formData ya sanitizado para repoblar el formulario de forma segura
                    formData: { nombre, email, telefono, servicio_id, mensaje }
                });
            }

            // --- Guardar en BD ---
            const archivo = req.file ? req.file.filename : null;

            const id = await Solicitud.create({
                nombre,
                email,
                telefono,
                servicio_id: parseInt(servicio_id),
                archivo,
                mensaje
            });

            if (isAjax) {
                return res.status(201).json({
                    success: true,
                    id,
                    message: 'Solicitud registrada correctamente.'
                });
            }

            return res.redirect('/contacto?exito=true&id=' + id);

        } catch (e) {
            if (isAjax) {
                return res.status(500).json({
                    success: false,
                    message: 'Error interno del servidor.'
                });
            }
            next(e);
        }
    },

    getDashboard: async (req, res, next) => {
        try {
            res.render('dashboard', { titulo: 'Dashboard' });
        } catch (e) {
            next(e);
        }
    },

    getDashboardData: async (req, res, next) => {
        try {
            const [
                totalSolicitudes,
                servicioMasPedido,
                ultimasSolicitudes,
                estados,
                solicitudesPorServicio,
                totalServicios
            ] = await Promise.all([
                Solicitud.count(),
                Solicitud.getMostRequested(),
                Solicitud.getLast(5),
                Solicitud.countByStatus(),
                Solicitud.getByService(),
                Servicio.count()
            ]);

            res.json({
                success: true,
                data: {
                    totalSolicitudes,
                    totalServicios,
                    servicioMasPedido: servicioMasPedido || { nombre: 'Sin datos', total: 0 },
                    ultimasSolicitudes,
                    estados,
                    solicitudesPorServicio
                }
            });

        } catch (e) {
            next(e);
        }
    }
};

module.exports = solicitudController;
