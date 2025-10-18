#!/bin/bash

# QUICK IMAGE SETUP SCRIPT
# Run this after downloading the 6 images from the chat

echo "========================================="
echo "WARPEED PROTECTION SYSTEM IMAGE SETUP"
echo "========================================="
echo ""

WEBSITE_DIR="/Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/website"

echo "INSTRUCCIONES:"
echo ""
echo "1. Descarga las 6 imágenes del chat a Downloads"
echo "2. Este script las renombrará automáticamente"
echo ""
echo "Presiona ENTER cuando hayas descargado las imágenes..."
read

cd ~/Downloads

echo ""
echo "Buscando imágenes recientes en Downloads..."
echo ""

# Find the 6 most recent PNG files
IMAGES=($(ls -t *.png 2>/dev/null | head -6))

if [ ${#IMAGES[@]} -lt 6 ]; then
    echo "❌ ERROR: Solo se encontraron ${#IMAGES[@]} imágenes PNG recientes."
    echo "Por favor descarga las 6 imágenes del chat primero."
    exit 1
fi

echo "✓ Encontradas ${#IMAGES[@]} imágenes:"
for img in "${IMAGES[@]}"; do
    echo "  - $img"
done
echo ""

echo "Estas imágenes serán renombradas como:"
echo "  1. ${IMAGES[0]} → protection-comparison.png (Comparación antes/después)"
echo "  2. ${IMAGES[1]} → protection-layer-cross-section.png (Vista en corte)"
echo "  3. ${IMAGES[2]} → protection-sail-isometric.png (Vista 3D)"
echo "  4. ${IMAGES[3]} → protection-cell-architecture.png (Blueprint celdas)"
echo "  5. ${IMAGES[4]} → protection-comparison.png (Duplicada - saltada)"
echo "  6. ${IMAGES[5]} → protection-self-healing-microscopic.png (Vista microscópica)"
echo ""
echo "¿Continuar? (y/n): "
read CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "Operación cancelada."
    exit 0
fi

echo ""
echo "Copiando y renombrando imágenes..."

# Copy and rename images
cp "${IMAGES[0]}" "$WEBSITE_DIR/protection-comparison.png"
echo "✓ protection-comparison.png"

cp "${IMAGES[1]}" "$WEBSITE_DIR/protection-layer-cross-section.png"
echo "✓ protection-layer-cross-section.png"

cp "${IMAGES[2]}" "$WEBSITE_DIR/protection-sail-isometric.png"
echo "✓ protection-sail-isometric.png"

cp "${IMAGES[3]}" "$WEBSITE_DIR/protection-cell-architecture.png"
echo "✓ protection-cell-architecture.png"

# Skip image 4 (duplicate of image 0)

cp "${IMAGES[5]}" "$WEBSITE_DIR/protection-self-healing-microscopic.png"
echo "✓ protection-self-healing-microscopic.png"

echo ""
echo "========================================="
echo "✅ COMPLETADO!"
echo "========================================="
echo ""
echo "5 imágenes instaladas en:"
echo "$WEBSITE_DIR"
echo ""
echo "Ahora puedes abrir material.html en tu navegador."
echo ""
