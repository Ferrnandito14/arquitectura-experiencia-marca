import { Composio } from '@composio/core';

// El SDK lee COMPOSIO_API_KEY del entorno. No se pasa en el código.
const composio = new Composio();

function idUsuario(): string {
  const id = process.env.COMPOSIO_USER_ID;
  if (!id) {
    throw new Error('Falta COMPOSIO_USER_ID: el identificador estable del usuario actual.');
  }
  return id;
}

/** Sesión de Composio del usuario actual, limitada al toolkit de Instagram. */
export async function crearSesionInstagram() {
  return composio.sessions.create(idUsuario(), {
    toolkits: ['instagram'],
    manageConnections: true,
  });
}

/** Herramientas de la sesión, listas para pasarlas al agente. */
export async function herramientasInstagram() {
  const session = await crearSesionInstagram();
  return { session, tools: await session.tools() };
}
