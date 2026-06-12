const express = require('express');
const router = express.Router();

const servicioController = require('../controllers/servicioController');
const solicitudController = require('../controllers/solicitudController');

const { upload, handleUploadError } = require('../middleware/upload');

// Página principal
router.get('/', servicioController.getIndex);

// Nuevas páginas
router.get('/nosotros', servicioController.getNosotros);
router.get('/servicios', servicioController.getServiciosPage);
router.get('/contacto', servicioController.getContacto);

// Dashboard
router.get('/dashboard', solicitudController.getDashboard);

// APIs AJAX
router.get('/api/servicios', servicioController.getServiciosJSON);
router.get('/api/dashboard/data', solicitudController.getDashboardData);

// Formulario
router.post(
    '/solicitud',
    upload.single('archivo'),
    handleUploadError,
    solicitudController.postSolicitud
);

module.exports = router;
