<?php

use DI\Container;
use Psr\Container\ContainerInterface;
use Slim\Factory\AppFactory;

require __DIR__ . '/../vendor/autoload.php';

// Crear contenedor
$container = new Container();

// Registrar configuración
$container->set('settings', function () {
	$settings = require __DIR__ . '/../app/settings.php';
	return new \App\Settings\Settings($settings);
});


// Registrar conexión a base de datos
$container->set('db', function (ContainerInterface $container) {
	return new \App\Data\DataContext(
		$container->get('settings')->get()
	);
});

// Configurar Slim con el contenedor
AppFactory::setContainer($container);
$app = AppFactory::create();

// Cargar rutas
$routes = require __DIR__ . '/../app/routes.php';
$routes($app);

// Middlewares importantes
$app->addBodyParsingMiddleware();
$app->addRoutingMiddleware();
$app->addErrorMiddleware(true, true, true);

// Ejecutar app
$app->run();
