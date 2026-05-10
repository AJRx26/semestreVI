<?php

namespace App\Controllers;

use App\Data\DataContext;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Container\ContainerInterface;

class IncidenteController
{
	private DataContext $db;
	
	public function __construct(private ContainerInterface $container)
	{
		$this->db = $container->get('db');
	}

	public function guardar(Request $req, Response $res, $args)
	{
		$datos = $req->getParsedBody();
		$archivos = $req->getUploadedFiles();
		$nombreArchivo = null;

		if (isset($archivos['archivo-evidencia'])) {
			$archivo = $archivos['archivo-evidencia'];

			if ($archivo->getError() === UPLOAD_ERR_OK) {
				$nombreOriginal = $archivo->getClientFilename();
				$extension = pathinfo($nombreOriginal, PATHINFO_EXTENSION);
				$nombreArchivo = uniqid('evidencia_', true) . '.' . $extension;

				$rutaDestino = __DIR__ . '/../../public/uploads/' . $nombreArchivo;
				$archivo->moveTo($rutaDestino);
			}
		}
		
		$incidente = [
			'nombre' => $datos['nombre'] ?? '',
			'correo' => $datos['correo'] ?? '',
			'rol' => $datos['rol'] ?? '',
			'tipo' => $datos['tipo'] ?? '',
			'descripcion' => $datos['descripcion'] ?? '',
			'evidencia' => $nombreArchivo
		];

		$this->db->insertarIncidente($incidente);

		return $res
			->withHeader('Location', '/incidentes')
			->withStatus(302);
	}

	public function listar(Request $req, Response $res, $args)
	{
		$model = $this->db->obtenerIncidentes();

		ob_start();
		require __DIR__ . '/../Views/Incidente/Lista.php';
		$contenido = ob_get_clean();

		$res->getBody()->write($contenido);
		return $res;
	}
}
