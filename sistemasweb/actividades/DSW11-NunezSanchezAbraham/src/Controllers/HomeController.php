<?php

namespace App\Controllers;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Container\ContainerInterface;

class HomeController
{
	public function __construct(private ContainerInterface $container)
	{
	}

	public function index(Request $req, Response $res, $args)
	{
		ob_start();
		require __DIR__ . '/../Views/Home/Index.php';
		$contenido = ob_get_clean();

		$res->getBody()->write($contenido);
		return $res;
	}
}
