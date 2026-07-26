#!/bin/bash
# Script de despliegue para Oracle Cloud Infrastructure (OCI)
# Requisitos: Docker, OCI CLI configurado

set -e

echo "========================================"
echo "  Despliegue FarmaBot en OCI"
echo "========================================"

# Variables
REGION="us-ashburn-1"
REPO_NAME="farmaco-sustitucion"
INSTANCE_NAME="farmabot-server"

echo "1. Verificando OCI CLI..."
oci --version || { echo "OCI CLI no instalado"; exit 1; }

echo "2. Creando repositorio de contenedores en OCI Registry..."
oci artifacts container repository create \
    --display-name "$REPO_NAME" \
    --is-public true \
    --region "$REGION" || echo "  (puede que ya exista)"

echo "3. Construyendo imagen Docker..."
docker build -t "$REPO_NAME:latest" .

echo "4. Subiendo imagen a OCI Registry..."
TENANCY_NS=$(oci os ns get --query "data" --raw-output)
REGISTRY_URL="$REGION.ocir.io/$TENANCY_NS/$REPO_NAME"

docker tag "$REPO_NAME:latest" "$REGISTRY_URL:latest"
docker push "$REGISTRY_URL:latest"

echo "5. Creando instancia de compute..."
INSTANCE_ID=$(oci compute instance launch \
    --display-name "$INSTANCE_NAME" \
    --shape "VM.Standard.E2.1.Micro" \
    --subnet-id "$(oci network subnet list --query 'data[0].id' --raw-output)" \
    --image-id "$(oci compute image list --query "data[?contains(\\\"display-name\\\",'Canonical-Ubuntu-22.04')] | [0].id" --raw-output)" \
    --assign-public-ip true \
    --query "data.id" \
    --raw-output)

echo "6. Instancia lanzada: $INSTANCE_ID"
echo ""
echo "========================================"
echo "  Despliegue completado"
echo "========================================"
echo ""
echo "Pasos manuales restantes:"
echo "1. SSH a la instancia: oci compute instance connect --instance-id $INSTANCE_ID"
echo "2. Instalar Docker en la instancia"
echo "3. Ejecutar: docker run -d -p 8501:8501 $REGISTRY_URL:latest"
echo "4. Abrir puerto 8501 en el security list de OCI"
echo ""
echo "Una vez desplegado, la app estará disponible en:"
echo "http://<IP_PUBLICA>:8501"
