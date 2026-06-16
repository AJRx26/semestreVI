const Servicio = require('../models/servicioModel');
const servicioController = {
    // Página principal
    getIndex: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAllWithCategoria();
            res.render('index', {
                titulo: 'SeguriTech', servicios
            });
        } catch (e) {
            next(e);
        }
    },
    // Página Nosotros
    getNosotros: (req, res) => {
        res.render('nosotros', {
            titulo: 'Nosotros'
        });
    },
    // Página Catálogo
    getServiciosPage: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAllWithCategoria();
            res.render('servicios', {
                titulo: 'ervicios',
                servicios
            });
        } catch (e) {
            next(e);
        }
    },
    // Página Contacto
    getContacto: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAllWithCategoria();
            res.render('contacto', {
                titulo: 'Contacto',
                servicios
            });
        } catch (e) {
            next(e);
        }
    },
    // API AJAX
    getServiciosJSON: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAllWithCategoria();
            res.json({
                success: true,
                data: servicios
            });
        } catch (e) {
            next(e);
        }
    }
};

module.exports = servicioController;
