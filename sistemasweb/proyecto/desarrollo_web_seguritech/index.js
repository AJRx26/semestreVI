require('dotenv').config();
const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const webRoutes = require('./routes/webRoutes');
app.use('/', webRoutes);

app.use((req, res) => {
    res.status(404).render('error', { titulo: 'No encontrado', mensaje: 'La página no existe.' });
});

app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).render('error', { titulo: 'Error', mensaje: 'Ocurrió un error.' });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log('Servidor en http://localhost:' + PORT);
    console.log('Red: http://0.0.0.0:' + PORT);
});
