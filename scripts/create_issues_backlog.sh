#!/usr/bin/env bash
set -euo pipefail

REPO="DRavainera/MComix"
MILESTONE_1="Iteracion 1"
MILESTONE_2="Iteracion 2"

# Soporte para entornos donde gh esta instalado en Windows pero no en PATH de bash.
if ! command -v gh >/dev/null 2>&1; then
  if [[ -x "/c/Program Files/GitHub CLI/gh.exe" ]]; then
    export PATH="/c/Program Files/GitHub CLI:$PATH"
  elif [[ -x "/mnt/c/Program Files/GitHub CLI/gh.exe" ]]; then
    export PATH="/mnt/c/Program Files/GitHub CLI:$PATH"
  fi
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI no esta instalado."
  echo "Instala gh y vuelve a ejecutar este script."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Error: no hay sesion activa en gh. Ejecuta: gh auth login"
  exit 1
fi

create_label() {
  local name="$1"
  local color="$2"
  local description="$3"
  gh label create "$name" --repo "$REPO" --color "$color" --description "$description" --force >/dev/null
}

ensure_milestone() {
  local title="$1"
  local description="$2"
  local number
  number="$(gh api "repos/$REPO/milestones?state=all&per_page=100" --jq ".[] | select(.title==\"$title\") | .number" || true)"
  if [[ -z "$number" ]]; then
    echo "Creando milestone: $title"
    gh api "repos/$REPO/milestones" -X POST -f title="$title" -f description="$description" -f state="open" >/dev/null
  else
    echo "Milestone ya existe: $title"
  fi
}

issue_exists() {
  local title="$1"
  local number
  number="$(gh issue list --repo "$REPO" --state all --limit 500 --json number,title --jq ".[] | select(.title==\"$title\") | .number" || true)"
  [[ -n "$number" ]]
}

create_issue() {
  local title="$1"
  local labels="$2"
  local milestone="$3"
  local body="$4"

  if issue_exists "$title"; then
    echo "Saltando issue existente: $title"
    return
  fi

  echo "Creando issue: $title"
  gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body "$body" \
    --label "$labels" \
    --milestone "$milestone" >/dev/null
}

echo "Creando/actualizando labels..."
create_label "area:core" "1D76DB" "Nucleo de aplicacion"
create_label "area:ui" "5319E7" "Interfaz de usuario"
create_label "area:archive" "0052CC" "Soporte de archivos comprimidos"
create_label "area:library" "0E8A16" "Modulo de biblioteca"
create_label "area:packaging" "FBCA04" "Empaquetado y distribucion"
create_label "area:linux" "C2E0C6" "Compatibilidad Linux"
create_label "area:tests" "BFDADC" "Pruebas"
create_label "area:docs" "0075CA" "Documentacion"
create_label "area:ci" "D4C5F9" "Integracion continua"
create_label "priority:high" "B60205" "Alta prioridad"
create_label "priority:medium" "D93F0B" "Prioridad media"
create_label "size:S" "0E8A16" "Tamano pequeno"
create_label "size:M" "FBCA04" "Tamano mediano"
create_label "size:L" "D93F0B" "Tamano grande"
create_label "type:refactor" "C5DEF5" "Refactor"
create_label "type:bug" "D73A4A" "Correccion de bug"
create_label "type:chore" "F9D0C4" "Mantenimiento"
create_label "type:docs" "0075CA" "Trabajo de documentacion"

echo "Creando milestones..."
ensure_milestone "$MILESTONE_1" "Estabilizacion de runtime y compatibilidad Linux base"
ensure_milestone "$MILESTONE_2" "Desacople estructural, empaquetado y CI multi-entorno"

create_issue \
  "Fix carga i18n en Python 3 y manejo bytes/str" \
  "area:core,priority:high,size:M,type:bug" \
  "$MILESTONE_1" \
  "Objetivo: corregir carga de traducciones .mo y endurecer conversiones bytes/str en runtime.

Acceptance Criteria:
- Cambio de idioma funciona en arranque y runtime sin errores.
- Fallback de locale definido cuando faltan recursos.
- Tests de i18n agregados y en verde."

create_issue \
  "Refactor de preferencias: compatibilidad y serializacion estable" \
  "area:core,priority:high,size:M,type:refactor" \
  "$MILESTONE_1" \
  "Objetivo: unificar lectura/escritura de preferencias y eliminar rutas legacy fragiles.

Acceptance Criteria:
- Lectura/escritura idempotente.
- Migracion de formato sin perdida de datos.
- Tests para casos corruptos/incompletos."

create_issue \
  "Bootstrap robusto: validacion de dependencias y errores accionables" \
  "area:core,priority:high,size:M,type:chore" \
  "$MILESTONE_1" \
  "Objetivo: mejorar run/process para detectar faltantes y mostrar mensajes claros.

Acceptance Criteria:
- Error messages incluyen dependencia faltante y comando sugerido.
- Arranque no crashea por edge cases.
- Smoke tests de arranque y apertura basica pasan."

create_issue \
  "Desacoplar FileHandler por responsabilidades" \
  "area:core,priority:high,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: separar apertura, navegacion y estado interno de file_handler.py.

Acceptance Criteria:
- APIs internas claras y sin ciclos innecesarios.
- Abrir/siguiente/anterior sin regresion.
- Complejidad del modulo reducida."

create_issue \
  "Reducir acoplamiento de MainWindow" \
  "area:ui,priority:high,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: extraer logica de negocio de main.py hacia servicios/controladores.

Acceptance Criteria:
- main.py enfocado en orquestacion UI.
- Menor dependencia directa entre subsistemas.
- Flujo UI principal permanece estable."

create_issue \
  "Modularizar manejo de eventos (teclado/raton/DnD)" \
  "area:ui,priority:high,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: dividir event.py en componentes por dominio de evento.

Acceptance Criteria:
- Modulos de eventos separados y testeables.
- Sin regresion en atajos y navegacion.
- Complejidad ciclomatica reducida."

create_issue \
  "Refactor pipeline de imagen y normalizacion de errores" \
  "area:core,priority:high,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: reorganizar image_tools/image_handler para flujo coherente de transformaciones.

Acceptance Criteria:
- EXIF, rotacion, escala y transparencia sin regresiones.
- test_image_tools en verde.
- Errores de procesamiento estandarizados."

create_issue \
  "Estandarizar contrato de handlers de archivos comprimidos" \
  "area:archive,priority:medium,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: unificar interfaz de handlers internos/externos y gestion de fallos.

Acceptance Criteria:
- Contrato unico documentado para handlers.
- Soporte cifrado y solid archives intacto.
- test_archives pasa completo."

create_issue \
  "Mejorar cancelacion y concurrencia en workers" \
  "area:core,priority:medium,size:M,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: robustecer cancelacion/timeouts en workers y tareas de thumbnails/extraccion.

Acceptance Criteria:
- Cancelacion no deja hilos colgados.
- Navegacion rapida no bloquea UI.
- Test de estres basico agregado."

create_issue \
  "Separar capas en modulo Library (SQL/dominio/UI)" \
  "area:library,priority:medium,size:L,type:refactor" \
  "$MILESTONE_2" \
  "Objetivo: aislar consultas SQL y logica de dominio de la capa visual de biblioteca.

Acceptance Criteria:
- Consultas encapsuladas y reutilizables.
- UI de biblioteca conserva comportamiento.
- Rendimiento de carga no empeora."

create_issue \
  "Modernizar empaquetado Python y manifiesto" \
  "area:packaging,priority:medium,size:M,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: actualizar flujo de empaquetado y revisar metadatos versionados.

Acceptance Criteria:
- Build sdist/wheel reproducible.
- MANIFEST.in consistente con arbol actual.
- Instalacion local validada."

create_issue \
  "Actualizar documentacion tecnica y de uso" \
  "area:docs,priority:medium,size:S,type:docs" \
  "$MILESTONE_2" \
  "Objetivo: alinear README y notas con estado real de dependencias y ejecucion.

Acceptance Criteria:
- Guia de instalacion actualizada.
- Seccion troubleshooting incluida.
- Pasos validados en entorno limpio."

create_issue \
  "Definir estrategia de distribucion Windows (modernizar o deprecar)" \
  "area:packaging,priority:medium,size:M,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: revisar scripts win32 legacy y decidir roadmap explicito.

Acceptance Criteria:
- Decision documentada en repo.
- Si se mantiene: pipeline funcional.
- Si se depreca: aviso y alternativas documentadas."

create_issue \
  "Ampliar suite de regresion para rutas criticas" \
  "area:tests,priority:high,size:M,type:chore" \
  "$MILESTONE_1" \
  "Objetivo: agregar pruebas para i18n, preferencias, apertura, render y navegacion.

Acceptance Criteria:
- Nuevos tests reproducibles en CI.
- Cobertura incrementada en modulos criticos.
- Flakiness controlada."

create_issue \
  "Configurar quality gate en CI (lint + tests)" \
  "area:ci,priority:medium,size:S,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: crear pipeline de validacion automatica para PRs.

Acceptance Criteria:
- PR falla ante regresiones.
- Reporte de calidad visible.
- Tiempo de pipeline razonable."

create_issue \
  "Definir matriz de dependencias Linux por distro" \
  "area:linux,priority:high,size:S,type:docs" \
  "$MILESTONE_1" \
  "Objetivo: documentar paquetes minimos para Debian/Ubuntu, Fedora y Arch.

Acceptance Criteria:
- Tabla por distro con nombres de paquete.
- Versiones minimas definidas.
- Verificado en VM/contenedor."

create_issue \
  "Fallbacks Linux para binarios externos (7z/unrar/mutool)" \
  "area:linux,priority:high,size:M,type:bug" \
  "$MILESTONE_1" \
  "Objetivo: detectar herramientas opcionales y degradar funcionalidad sin crashear.

Acceptance Criteria:
- Mensajes indican exactamente que instalar.
- Funciones no dependientes siguen operativas.
- Pruebas de deteccion por binario."

create_issue \
  "Migrar rutas a estandar XDG" \
  "area:linux,priority:high,size:M,type:refactor" \
  "$MILESTONE_1" \
  "Objetivo: usar XDG_CONFIG_HOME, XDG_CACHE_HOME y XDG_DATA_HOME para config/cache/data.

Acceptance Criteria:
- Escritura en rutas XDG.
- Migracion automatica desde rutas antiguas.
- Sin perdida de preferencias."

create_issue \
  "Validar integracion desktop y MIME en Linux" \
  "area:linux,priority:medium,size:M,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: revisar .desktop, appdata, mime.xml y thumbnailer.

Acceptance Criteria:
- Asociacion .cbz/.cbr funcional.
- Miniaturas generadas correctamente.
- Metadata desktop valida con herramientas estandar."

create_issue \
  "Compatibilidad Wayland/X11 para UI critica" \
  "area:linux,priority:medium,size:M,type:bug" \
  "$MILESTONE_2" \
  "Objetivo: probar y ajustar clipboard, cursor, DnD y OSD en ambos backends.

Acceptance Criteria:
- Sin crash en GNOME/KDE.
- Clipboard y DnD operativos en Wayland y X11.
- Hallazgos documentados."

create_issue \
  "Empaquetado Linux distribuible (wheel + Flatpak/AppImage)" \
  "area:linux,priority:medium,size:L,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: definir y automatizar al menos un formato de distribucion Linux.

Acceptance Criteria:
- Artefacto instalable en distro limpia.
- Arranque y apertura basica validados.
- Guia de instalacion incluida."

create_issue \
  "CI Linux multi-entorno" \
  "area:linux,area:ci,priority:medium,size:M,type:chore" \
  "$MILESTONE_2" \
  "Objetivo: pipeline para Ubuntu/Fedora (matrix o contenedores) con tests.

Acceptance Criteria:
- Tests corren automaticamente en Linux.
- Reporte por entorno y version Python.
- PR bloqueado ante fallos Linux."

create_issue \
  "Documentacion Linux completa (instalacion y troubleshooting)" \
  "area:linux,area:docs,priority:high,size:S,type:docs" \
  "$MILESTONE_1" \
  "Objetivo: anadir seccion dedicada con comandos por distro y resolucion de problemas.

Acceptance Criteria:
- Pasos reproducibles en entorno limpio.
- Troubleshooting para GTK/binarios externos.
- Enlaces y comandos verificados."

echo "Listo. Issues creados/asignados en $REPO"
