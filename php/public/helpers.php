<?php

if (!function_exists('portal_url')) {
    function portal_url(): string
    {
        $scheme = getenv('PORTAL_SCHEME') ?: 'http';
        $host = getenv('PORTAL_HOST') ?: 'localhost';
        $host = $host !== '' ? $host : 'localhost';

        $port = getenv('PORTAL_PORT');
        if ($port === false || $port === null || trim($port) === '') {
            $port = '3000';
        }
        $port = trim((string) $port);

        $defaultPort = $scheme === 'https' ? '443' : '80';
        $portPart = ($port !== '' && $port !== $defaultPort) ? ':' . $port : '';

        return sprintf('%s://%s%s', $scheme, $host, $portPart);
    }
}
