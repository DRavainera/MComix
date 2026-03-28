# Guia de trabajo por issue

Usar esta lista al iniciar y cerrar cada issue del backlog.

## 1) Inicio
- [ ] Leer descripcion del issue y criterios de aceptacion.
- [ ] Confirmar milestone correcto (Iteracion 1 o Iteracion 2).
- [ ] Crear rama con nombre `tipo/ID-resumen-corto`.
- [ ] Identificar modulos afectados y riesgos de regresion.

## 2) Implementacion
- [ ] Hacer cambios acotados al alcance del issue.
- [ ] Evitar mezclar refactors no relacionados.
- [ ] Mantener compatibilidad con flujo actual de usuario.
- [ ] Agregar o ajustar tests del area tocada.

## 3) Validacion tecnica
- [ ] Ejecutar tests relevantes del modulo.
- [ ] Ejecutar suite completa si el cambio es transversal.
- [ ] Verificar arranque y flujo basico: abrir, navegar, zoom.
- [ ] Si aplica Linux: validar en distro objetivo y documentar resultado.

## 4) Preparacion de PR
- [ ] Completar `pull_request_template.md`.
- [ ] Copiar criterios de aceptacion y marcarlos uno por uno.
- [ ] Adjuntar comandos ejecutados y resultados.
- [ ] Declarar riesgos, mitigacion y rollback.

## 5) Cierre del issue
- [ ] Confirmar que todos los criterios estan cumplidos.
- [ ] Vincular PR al issue (`Closes #ID`).
- [ ] Mover estado/milestone si hubo cambio de alcance.
- [ ] Documentar follow-ups en nuevos issues (no en comentarios sueltos).

## Checklist rapido Linux
- [ ] Dependencias del sistema instaladas.
- [ ] Binarios externos detectados o fallback funcionando.
- [ ] Rutas XDG respetadas (si aplica).
- [ ] Integracion MIME/desktop validada (si aplica).
- [ ] Wayland/X11 validado para cambios de UI (si aplica).
