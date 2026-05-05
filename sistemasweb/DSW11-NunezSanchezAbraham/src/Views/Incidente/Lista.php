<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incidentes registrados</title>
    <link rel="stylesheet" href="/css/estilos.css">
</head>

<body>
    <main id="contenido">
        <section>
            <h1>Incidentes registrados</h1>
            <p><a href="/">Volver al portal</a></p>

            <?php if (count($model) === 0): ?>
                <p>No existen incidentes registrados.</p>
            <?php else: ?>
                <?php foreach ($model as $incidente): ?>
                    <article class="aviso">
                        <h2><?= htmlspecialchars($incidente->tipo) ?></h2>
                        <p><strong>Nombre:</strong> <?= htmlspecialchars($incidente->nombre)?></p>
                        <p><strong>Correo:</strong> <?= htmlspecialchars($incidente->correo)?></p>
                        <p><strong>Rol:</strong> <?= htmlspecialchars($incidente->rol)?></p>
                        <p><strong>Descripción:</strong> <?= htmlspecialchars($incidente->descripcion)?></p>
                        <p><strong>Fecha:</strong> <?= htmlspecialchars($incidente->fecha_registro)?></p>
                        <?php if (!empty($incidente->evidencia)): ?>
                            <p>
                                <strong>Evidencia:</strong>
                                <a href="/uploads/<?=htmlspecialchars($incidente->evidencia) ?>" target="_blank">
                                        Ver archivo
                                </a>
                            </p>
                        <?php endif; ?>
                    </article>
                <?php endforeach; ?>
            <?php endif; ?>
        </section>
    </main>
</body>
</html>

