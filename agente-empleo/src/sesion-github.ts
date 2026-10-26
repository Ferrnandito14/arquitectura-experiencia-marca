import { readFileSync } from 'node:fs';
import { Composio } from '@composio/core';

// Escritura en el repo a través de Composio (GitHub conectado), sin depender de git push.
// Se usa en las tareas programadas, cuyo proxy de git no permite subir cambios.
const composio = new Composio();

const DUENO = process.env.REPO_DUENO ?? 'Ferrnandito14';
const REPO = process.env.REPO_NOMBRE ?? 'arquitectura-experiencia-marca';
const RAMA = process.env.REPO_RAMA ?? 'claude/funny-clarke-e1d7h3';
const RAIZ = new URL('../../', import.meta.url); // raíz del repo (carpeta que contiene agente-empleo/)

const TEXTO = /\.(json|md|txt|ts|py|csv)$/i;

/** Sube archivos (rutas relativas a la raíz del repo) en un solo commit a la rama de trabajo. */
export async function subirArchivos(mensaje: string, rutas: string[], borrar: string[] = []) {
  const session = await composio.sessions.create(process.env.COMPOSIO_USER_ID ?? '', { toolkits: ['github'], manageConnections: true });
  const upserts = rutas.map((ruta) => {
    const datos = readFileSync(new URL(ruta, RAIZ));
    return TEXTO.test(ruta)
      ? { path: ruta, content: datos.toString('utf8'), encoding: 'utf-8' }
      : { path: ruta, content: datos.toString('base64'), encoding: 'base64' };
  });
  const r = await session.execute('GITHUB_COMMIT_MULTIPLE_FILES', {
    owner: DUENO,
    repo: REPO,
    branch: RAMA,
    message: `${mensaje}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`,
    upserts,
    deletes: borrar,
    max_retries: 3,
  });
  if (r.error) throw new Error('GITHUB_COMMIT_MULTIPLE_FILES: ' + r.error);
  return r.data as Record<string, any>;
}
