# agente-empleo

Sesión de Composio limitada al toolkit de LinkedIn, para pasar sus herramientas al agente.

- `src/sesion-linkedin.ts`: crea la sesión (`toolkits: ['linkedin']`) y expone `herramientasLinkedin()`.
- `src/verificar-linkedin.ts`: autoriza LinkedIn si hace falta y hace una llamada de solo lectura (`LINKEDIN_WHO_AM_I`).

## Uso

Variables de entorno (nunca en el repo): `COMPOSIO_API_KEY` y `COMPOSIO_USER_ID`.

```
npm install
npm run verificar
```

El toolkit de LinkedIn tiene herramientas de perfil, publicaciones y estadísticas. No incluye búsqueda de empleo.
