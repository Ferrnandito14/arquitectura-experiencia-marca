import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { crearSesionInstagram } from './sesion-instagram.js';

// Operador de la cuenta de Instagram a través de Composio (API oficial).
//   publicar-pendientes   publica las piezas de la cola cuya hora ya llegó
//   contenedor-prueba     crea un contenedor de imagen sin publicarlo (prueba)
//   comentarios-nuevos    lista comentarios sin atender en las últimas publicaciones
//   responder <id> <txt>  responde a un comentario de una publicación propia
// Variables de entorno: COMPOSIO_API_KEY, COMPOSIO_USER_ID.

const COLA = new URL('../../cuenta-hamsterverified/cola.json', import.meta.url);
const ATENDIDOS = new URL('../../cuenta-hamsterverified/comentarios-atendidos.json', import.meta.url);

type Pieza = {
  id: string;
  programada: string; // ISO 8601 con zona, por ejemplo 2026-10-25T09:30:00-04:00
  tipo: 'imagen' | 'carrusel' | 'reel';
  urls: string[]; // JPEG para imagen y carrusel, MP4 para reel
  texto: string;
  estado: 'pendiente' | 'publicada' | 'error';
  ig_media_id?: string;
  error?: string;
};

const session = await crearSesionInstagram();

async function ejecutar(slug: string, args: Record<string, unknown>) {
  const r = await session.execute(slug, args);
  if (r.error) throw new Error(`${slug}: ${r.error}`);
  return r.data as Record<string, any>;
}

function idDe(d: Record<string, any>): string {
  const id = d.id ?? d.creation_id ?? d.data?.id ?? d.response_data?.id;
  if (!id) throw new Error('Respuesta sin id: ' + JSON.stringify(d).slice(0, 400));
  return String(id);
}

async function idCuenta(): Promise<string> {
  return String((await ejecutar('INSTAGRAM_GET_USER_INFO', {})).id);
}

async function publicar(p: Pieza, ig: string): Promise<string> {
  let creacion: string;
  if (p.tipo === 'imagen') {
    creacion = idDe(await ejecutar('INSTAGRAM_POST_IG_USER_MEDIA', { ig_user_id: ig, image_url: p.urls[0], caption: p.texto }));
  } else if (p.tipo === 'carrusel') {
    creacion = idDe(await ejecutar('INSTAGRAM_CREATE_CAROUSEL_CONTAINER', { ig_user_id: ig, child_image_urls: p.urls, caption: p.texto, share_to_feed: true }));
  } else {
    creacion = idDe(await ejecutar('INSTAGRAM_POST_IG_USER_MEDIA', { ig_user_id: ig, video_url: p.urls[0], media_type: 'REELS', caption: p.texto, share_to_feed: true }));
  }
  const pub = await ejecutar('INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH', { ig_user_id: ig, creation_id: creacion, max_wait_seconds: 180 });
  return idDe(pub);
}

const [orden, ...resto] = process.argv.slice(2);

if (orden === 'publicar-pendientes') {
  const cola: Pieza[] = JSON.parse(readFileSync(COLA, 'utf8'));
  const ahora = Date.now();
  const ig = await idCuenta();
  for (const p of cola.filter((x) => x.estado === 'pendiente' && Date.parse(x.programada) <= ahora)) {
    try {
      p.ig_media_id = await publicar(p, ig);
      p.estado = 'publicada';
      console.log('publicada', p.id, p.ig_media_id);
    } catch (e) {
      p.estado = 'error';
      p.error = String(e).slice(0, 300);
      console.log('error', p.id, p.error);
    }
    writeFileSync(COLA, JSON.stringify(cola, null, 2) + '\n');
  }
  console.log('pendientes restantes:', cola.filter((x) => x.estado === 'pendiente').length);
} else if (orden === 'contenedor-prueba') {
  const ig = await idCuenta();
  const d = await ejecutar('INSTAGRAM_POST_IG_USER_MEDIA', { ig_user_id: ig, image_url: resto[0], caption: resto[1] ?? 'prueba #esencia' });
  console.log('contenedor creado (sin publicar):', JSON.stringify(d).slice(0, 400));
} else if (orden === 'comentarios-nuevos') {
  const ig = await idCuenta();
  const vistos: string[] = existsSync(ATENDIDOS) ? JSON.parse(readFileSync(ATENDIDOS, 'utf8')) : [];
  const medios = await ejecutar('INSTAGRAM_GET_IG_USER_MEDIA', { ig_user_id: ig, limit: 10, fields: 'id,caption,permalink,timestamp' });
  const lista: any[] = medios.data ?? medios.items ?? [];
  const nuevos: unknown[] = [];
  for (const m of lista) {
    const c = await ejecutar('INSTAGRAM_GET_IG_MEDIA_COMMENTS', { ig_media_id: m.id, limit: 50, fields: 'id,text,username,timestamp' });
    for (const k of (c.data ?? c.items ?? []) as any[]) {
      if (!vistos.includes(k.id)) nuevos.push({ comentario: k.id, usuario: k.username, texto: k.text, publicacion: m.permalink });
    }
  }
  console.log(JSON.stringify(nuevos, null, 2));
} else if (orden === 'responder') {
  const [idComentario, ...texto] = resto;
  await ejecutar('INSTAGRAM_POST_IG_COMMENT_REPLIES', { ig_comment_id: idComentario, message: texto.join(' ') });
  const vistos: string[] = existsSync(ATENDIDOS) ? JSON.parse(readFileSync(ATENDIDOS, 'utf8')) : [];
  writeFileSync(ATENDIDOS, JSON.stringify([...vistos, idComentario], null, 2) + '\n');
  console.log('respondido', idComentario);
} else {
  console.log('Órdenes: publicar-pendientes | contenedor-prueba <url_jpg> [texto] | comentarios-nuevos | responder <id> <texto>');
}
