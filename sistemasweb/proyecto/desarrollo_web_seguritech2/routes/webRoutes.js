const express = require('express');
const router = express.Router();
const servicioController = require('../controllers/servicioController');
const solicitudController = require('../controllers/solicitudController');
const { upload, handleUploadError } = require('../middleware/upload');

router.get('/', servicioController.getIndex);
router.get('/dashboard', solicitudController.getDashboard);
router.get('/api/servicios', servicioController.getServiciosJSON);
router.get('/api/dashboard/data', solicitudController.getDashboardData);
router.post('/solicitud', upload.single('archivo'), handleUploadError, solicitudController.postSolicitud);

module.exports = router;
