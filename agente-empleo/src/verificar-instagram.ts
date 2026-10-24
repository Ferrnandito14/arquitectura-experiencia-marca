import { crearSesionInstagram } from './sesion-instagram.js';

const session = await crearSesionInstagram();

const { items } = await session.toolkits();
const instagram = items.find((t) => t.slug === 'instagram');
if (!instagram?.connection?.isActive) {
  const solicitud = await session.authorize('instagram');
  console.log('Abre este enlace para autorizar Instagram:');
  console.log(solicitud.redirectUrl);
  await solicitud.waitForConnection(600_000);
}

// Llamada de solo lectura: perfil y estadísticas de la cuenta conectada.
const resultado = await session.execute('INSTAGRAM_GET_USER_INFO', {});
console.log('error:', resultado.error);
console.log('campos recibidos:', Object.keys(resultado.data));
console.log('logId:', resultado.logId);
