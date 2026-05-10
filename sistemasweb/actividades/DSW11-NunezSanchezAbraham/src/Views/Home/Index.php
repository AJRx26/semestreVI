<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <link rel="icon" href="data:,">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Portal institucional: avisos, servicios, horarios, indicadores y contacto.">
    <title> Portal Instituional | Centro de Cómputo</title>
    <link rel="stylesheet" href="css/estilos.css">
    <script src="js/script.js" defer></script>
</head>

<body>
    <div class="layout-principal">

        <header>
            <img id="logo-fei" src="img/logo-fei.jpeg" alt="Logo de la Facultad de Estadística e Informática">
            <div>
                <p><strong>Universidad Veracruzana</strong></p>
                <p>Facultad de Estadística e Informática</p>
            </div>

            <nav aria-label="Navegación principal">
                <a href="#avisos">Avisos</a>
                <a href="#servicios">Servicios</a>
                <a href="#horarios">Horarios</a>
                <a href="#indicadores">Indicadores</a>
                <a href="#contacto">Contacto</a>
            </nav>
        </header>

        <main id="contenido">

            <section id="panel-mensajes" aria-label="Mensajes dinámicos del portal">
                <h2>Estado del portal</h2>
                <p id="mensaje-dinamico">Bienvenido al Portal Institucional del Centro de Cómputo.</p>
            </section>

            <!-- HERO / PRESENTACIÓN -->
            <section aria-labelledby="titulo-portal">

                <h1 id="titulo-portal">Portal Institucional del Centro de Cómputo</h1>
                <p>
                    Información oficial sobre servicios, avisos, horarios de atención y recursos para la comunidad.
                    Esta página está construida con HTML semántico para facilitar accesibilidad, mantenimiento y SEO.
                </p>

                <p>
                    Accesos rápidos:
                    <a href="#servicios">Ver servicios</a>
                    <a href="#contacto"> Reportar incidente</a>
                </p>
            </section>

            <section id="galeria" aria-labelledby="galeria-titulo">
                <h2 id="galeria-titulo">Galería del Centro de Cómputo</h2>
                <img id="imagen-carrusel" src="img/centro-computo-2.jpg" alt="Imagen del Centro de Cómputo">
                <p id="descripcion-carrusel">Vista general del laboratorio.</p>
                <p>
                    <button type="button" id="btn-anterior">Anterior</button>
                    <button type="button" id="btn-siguiente">Siguiente</button>
                </p>
            </section>

            <!-- CONTENIDO PRINCIPAL EN DOS COLUMNAS LÓGICAS: ARTÍCULOS + ASIDE -->
            <section aria-label="Contenido principal del portal">
                <!-- BLOQUE DE ARTÍCULOS -->
                <section aria-label="Novedades y avisos">
                    <h2 id="avisos">Avisos y comunicados</h2>

                    <div id="lista-avisos"></div>
                </section>
            </section>

            <!-- SERVICIOS -->
            <section id="servicios" aria-labelledby="servicios-titulo">
                <h2 id="servicios-titulo">Servicios</h2>
                <p>Servicios disponibles para estudiantes, docentes y personal administrativo.</p>

                <article aria-labelledby="servicio-1">
                    <h3 id="servicio-1">Mesa de ayuda</h3>
                    <p>Atención de incidentes: conectividad, cuentas, software, periféricos y aulas.</p>
                </article>

                <article aria-labelledby="servicio-2">
                    <h3 id="servicio-2">Préstamo y resguardo de equipos</h3>
                    <p>Solicitud, control y seguimiento de préstamos temporales de equipo.</p>
                </article>

                <article aria-labelledby="servicio-3">
                    <h3 id="servicio-3">Mesa de ayuda</h3>
                    <p>Políticas de uso, horarios, lineamientos y buenas prácticas de seguridad.</p>
                </article>

                <!-- HORARIOS / TABLA -->
                <section id="horarios" aria-labelledby="horarios-titulo">
                    <h2 id="horarios-titulo">Horarios de atención</h2>
                    <p>Horarios referenciales. Conirma cambios en avisos.</p>

                    <table>
                        <caption>Horario de atención por servicio</caption>
                        <thead>
                            <tr>
                                <th scope="col">Servicio</th>
                                <th scope="col">Días</th>
                                <th scope="col">Horario</th>
                                <th scope="col">Ubicación</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Mesa de ayuda</td>
                                <td>Lunes a viernes</td>
                                <td>09:00 - 18:00</td>
                                <td>Edificio A - Planta Baja</td>
                            </tr>
                            <tr>
                                <td>Laboratorios</td>
                                <td>Lunes a sábado</td>
                                <td>07:00 - 20:00</td>
                                <td>Edificio B - Aulas de cómputo</td>
                            </tr>
                            <tr>
                                <td>Préstamo de equipo</td>
                                <td>Lunes a viernes</td>
                                <td>10:00 - 14:00</td>
                                <td>Centro de Cómputo</td>
                            </tr>
                        </tbody>
                    </table>
                </section>

                <!-- INDICADORES (LISTAS) -->
                <section id="indicadores" aria-labelledby="indicadores-titulo">
                    <h2 id="indicadores-titulo">Indicadores</h2>
                    <div id="panel-indicadores"></div>
                </section>

                <!-- CONTACTO / FORMULARIO -->
                <section id="contacto" aria-labelledby="contacto-titulo">
                    <h2 id="contacto-titulo">Contacto y reporte de incidente</h2>
                    <p>Completa el formulario para registrar una solicitud. (En próximas clases se validará con JavaScript.)</p>

                    <form id="formulario-contacto" action="/incidente/guardar" method="post" enctype="multipart/form-data" aria-label="Formulario de contacto">
                        <fieldset>
                            <legend>Datos del solicitante</legend>

                            <p>
                                <label for="nombre">Nombre completo</label><br>
                                <input type="text" id="nombre" name="nombre" required>
                            </p>

                            <p>
                                <label for="correo">Correo institucional</label><br>
                                <input type="email" id="correo" name="correo" required>
                            </p>

                            <p>
                                <label for="rol">Rol</label><br>
                                <select id="rol" name="rol" required>
                                    <option value="">Selecciona una opción</option>
                                    <option value="estudiante">Estudiante</option>
                                    <option value="docente">Docente</option>
                                    <option value="administrativo">Administrativo</option>
                                </select>
                            </p>
                        </fieldset>

                        <fieldset>
                            <legend>Detalle del incidente</legend>

                            <p>
                                <label for="tipo">Tipo de solicitud</label><br>
                                <select id="tipo" name="tipo" required>
                                    <option value="">Selecciona una opción</option>
                                    <option value="red">Red / Internet</option>
                                    <option value="cuenta">Cuenta / Acceso</option>
                                    <option value="software">Software</option>
                                    <option value="equipo">Equipo / Periféricos</option>
                                    <option value="otro">Otro</option>
                                </select>
                            </p>

                            <p>
                                <label for="descripcion">Descripción</label><br>
                                <textarea id="descripcion" name="descripcion" rows="5" required></textarea>
                            </p>
                            
                            <section id="evidencia" aria-labelledby="evidencia-titulo">
                                <h3 id="evidencia-titulo">Carga de evidencia</h3>
                                <p>Adjunta arcivo como evidencia del incidente.</p>
                                <div id="zona-arrastre" tabindex="0">
                                    Arrastra aquí un archivo o haz clic para seleccionarlo.
                                </div>

                                <input type="file" id="archivo-evidencia" name="archivo-evidencia" accept=".jpg,.jpeg,.png,.pdf,.doc,.docx">
                                <p id="archivo-seleccionado">Ningún archivo seleccionado.</p>
                            </section>

                            <p>
                                <button type="submit">Enviar</button>
                                <button type="reset">Limpiar</button>
                            </p>

                        </fieldset>
                    </form>
	            <p><a href="/incidentes">COnsultar incidentes registrados</a></p>
                    <p id="mensaje-formulario"></p>
                </section>

                <section id="json-formulario" aria-labelledby="json-formulario-titulo">
                    <h3 id="json-formulario-titulo">Datos del formulario en formato JSON</h3>
                    <pre id="salida-json"></pre>
                </section>
                
            </section>
        </main>

        <!-- ASIDE: ACCESO RÁPIDO / RECURSOS -->
        <aside aria-label="Recursos y enlaces institucionales">
            <h2>Recursos</h2>

            <section aria-label="Enlaces útiles">
                <h3>Enlaces útiles</h3>
                    <ul>
                        <li><a href="#">Reglamento de laboratorios</a></li>
                        <li><a href="#">Calendario académico</a></li>
                        <li><a href="#">Directorio</a></li>
                    </ul>
            </section>

            <section aria-label="Accesibilidad">
                <h3>Accesibilidad</h3>
                    <p>
                        Este portal busca seguir buenas prácticas de accesibilidad: estructura semántica, textos alternativos y formularios con etiquetas claras.
                    </p>
            </section>
        </aside>        

        <footer>
            <p><strong>Centro de Cómputo</strong> Facultad de Estadística e Informática</p>
            <p>
                <a href="#">Aviso de privacidad</a>
                <a href="#">Términos de uso</a>
            </p>
            <p> 2026 Universidad Veracruzana</p>
        </footer>

    </div>
</body>

</html>⏎
