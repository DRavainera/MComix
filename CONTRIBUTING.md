# Contributing

Gracias por contribuir a MComix.

## Flujo de trabajo
1. Sincroniza con `main`.
2. Crea una rama por issue: `tipo/ID-resumen-corto`.
3. Haz cambios pequenos y enfocados al alcance del issue.
4. Ejecuta validaciones locales.
5. Abre PR usando la plantilla y vincula el issue (`Closes #ID`).

## Plantillas y checklist
- PR template: `.github/pull_request_template.md`
- Checklist de ejecucion por issue: `.github/issue_work_checklist.md`
- Issue templates: `.github/ISSUE_TEMPLATE/`

## Reglas de alcance
- No mezclar cambios no relacionados en el mismo PR.
- Mantener compatibilidad con el flujo base: abrir, navegar y renderizar.
- Para cambios grandes en modulos core (`main`, `file_handler`, `event`, `image_tools`), dividir en PRs incrementales.

## Validacion minima obligatoria
- Ejecutar tests del area modificada.
- Si el cambio es transversal, ejecutar suite completa:
```bash
pytest
```
- Smoke test manual:
  - abrir archivo
  - navegar paginas
  - validar zoom/render

## Reglas Linux (si aplica)
- Verificar dependencias del sistema por distro objetivo.
- Confirmar comportamiento cuando falten binarios opcionales (`7z`, `unrar`, `mutool`).
- Respetar rutas XDG para config/cache/data.
- Validar Wayland/X11 en cambios de UI.

## Requisitos del PR
- Completar todos los campos de la plantilla.
- Marcar criterios de aceptacion uno por uno.
- Incluir comandos ejecutados y resultados.
- Declarar riesgos, mitigacion y plan de rollback.
