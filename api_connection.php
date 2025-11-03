<?php
// No token needed!
$data = [
    'project_id' => '123',
    'generation_type' => 'brand_kit',
    'prompts' => [
        'business_name' => 'My Business',
        'description' => '...'
    ]
];

// Simple call without authentication
$response = $client->generateBrandKit($data);
?>