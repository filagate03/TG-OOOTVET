#!/bin/bash

# Пересобираем фронтенд
cd frontend
rm -rf dist
npm run build

echo "Frontend rebuilt successfully!"