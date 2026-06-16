const multer = require('multer');
const path = require('path');
const fs = require('fs');
const uploadDir = path.join(__dirname, '..', process.env.UPLOAD_DIR || 'public/uploads');
// Evita que se suban archivos con formato .exe, js o php
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });
const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    //Renombrado seguro
    filename: (req, file, cb) => {
        const unique = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, 'seguritech-' + unique + path.extname(file.originalname).toLowerCase());
    }
});
const fileFilter = (req, file, cb) => {
    const allowedExts = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'];
    //Se ejecuta mime para validacion
    const allowedMimes = ['image/jpeg', 'image/png', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedExts.includes(ext) && allowedMimes.includes(file.mimetype)) cb(null, true);
    else cb(new Error('Solo JPG, PNG, PDF, DOC, DOCX'));
};
//Validacion de tamano
const upload = multer({ storage, fileFilter, limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE) || 5 * 1024 * 1024, files: 1 } });
const handleUploadError = (err, req, res, next) => {
    if (err instanceof multer.MulterError) {
        if (err.code === 'LIMIT_FILE_SIZE') return res.status(400).json({ success: false, message: 'Máximo 5MB.' });
        return res.status(400).json({ success: false, message: err.message });
    } else if (err) return res.status(400).json({ success: false, message: err.message });
    next();
};
module.exports = { upload, handleUploadError };
