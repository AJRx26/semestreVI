<?php

return function (array $settings) {
	$settings['db']['host'] = 'localhost';
	$settings['db']['database'] = 'centro_computo';
	$settings['db']['username'] = 'cc_user';
	$settings['db']['password'] = 'cc2026*';

	$settings['env'] = 'dev';

	return $settings;
};
