<?php

declare(strict_types=1);

header("Content-Type: application/json");

$path = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);

if ($path === "/health") {
    echo json_encode(["ok" => true]);
    exit;
}

echo json_encode([
    "name" => "php-api",
    "status" => "ok",
    "generatedBy" => "ProgressiveNodeX"
]);