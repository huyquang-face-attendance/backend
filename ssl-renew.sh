#!/bin/bash

COMPOSE="/usr/local/bin/docker-compose --no-ansi"
DOCKER="/usr/bin/docker"

cd /path/to/your/project
$COMPOSE run certbot renew --force-renewal
$COMPOSE restart nginx 