<?php

use Slim\App;

return function (App $app) {
	$app->get('/', 'App\Controllers\HomeController:index');
	$app->post('/incidente/guardar', 'App\Controllers\IncidenteController:guardar' );
	$app->get('/incidentes', 'App\Controllers\IncidenteController:listar');
};
