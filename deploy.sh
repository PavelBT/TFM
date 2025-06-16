#!/bin/bash

echo "📦 Actualizando código desde GitHub..."
git pull origin main

echo "🧹 Deteniendo contenedores actuales..."
docker-compose down

echo "🚀 Reconstruyendo y levantando contenedores..."
docker-compose up --build -d


