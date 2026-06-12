const Servicio = require('../models/servicioModel');
const servicioController = {
    getIndex: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAllWithCategoria();
            res.render('index', { titulo: 'SeguriTech', servicios });
        } catch (e) { next(e); }
    },
    getServiciosJSON: async (req, res, next) => {
        try {
            const servicios = await Servicio.getAll();
            res.json({ success: true, data: servicios });
        } catch (e) { next(e); }
    }
};
module.exports = servicioController;
