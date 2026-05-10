const express = require('express')
const dotenv = require('dotenv')
const app = express()

//primero carga la configuracion del archivo .env
//para que este disponible en las demas llamadas
dotenv.config();
//establece el motor de vistas a ejs
app.set('view engine', 'ejs')

//ruta de la URL raiz
const homeRouter = require('./routes/home')
app.use("/", homeRouter)
app.use('/home', homeRouter)

//middleware para el manejo de errores (debe de ser el ultimo middleware a utilizar)
const errorhandler = require('./middlewares/errorhandler')
app.use(errorhandler)

//inicia el servidor web en el puerto SERVER_PORT
app.listen(process.env.SERVER_PORT, () => {
	console.log(`Aplicacion de ejemplo escuchando en el puerto ${process.env.SERVER_PORT}`)
})


