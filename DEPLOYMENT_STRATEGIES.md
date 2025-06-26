# Estrategias adicionales de almacenamiento para ejecutables

## 1. GitHub Releases (YA CONFIGURADO)
- Los ejecutables se suben automáticamente cuando haces un tag v*
- Ejemplo: `git tag v1.0.0 && git push origin v1.0.0`
- Disponible en: https://github.com/tu-usuario/tu-repo/releases

## 2. Almacenamiento en Branch dedicado
# Agregar al workflow después de la compilación:

- name: Subir a branch releases
  if: github.ref == 'refs/heads/main'
  run: |
    git config --global user.name 'github-actions[bot]'
    git config --global user.email 'github-actions[bot]@users.noreply.github.com'
    
    # Crear/actualizar branch releases
    git checkout -B releases
    
    # Copiar solo los archivos compilados
    mkdir -p releases
    cp -r dist/* releases/ || true
    cp *.zip releases/ || true
    
    # Commit y push
    git add releases/
    git commit -m "Auto-update releases $(date -u +%Y-%m-%d)" || true
    git push origin releases --force

## 3. Subir a S3/CloudFlare R2/Google Cloud Storage
# Requiere configurar secrets para las credenciales

## 4. FTP/SFTP a servidor propio
# Usando lftp o rsync

## 5. Artefactos de larga duración en repositorio separado
# Crear un repo dedicado solo para binarios
