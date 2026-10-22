import { crearSesionLinkedin } from './sesion-linkedin.js';

const session = await crearSesionLinkedin();

const { items } = await session.toolkits();
const linkedin = items.find((t) => t.slug === 'linkedin');
if (!linkedin?.connection?.isActive) {
  const solicitud = await session.authorize('linkedin');
  console.log('Abre este enlace para autorizar LinkedIn:');
  console.log(solicitud.redirectUrl);
  await solicitud.waitForConnection();
}

// Llamada de solo lectura: devuelve el nombre y el correo de la cuenta conectada.
const resultado = await session.execute('LINKEDIN_WHO_AM_I', {});
console.log('error:', resultado.error);
console.log('campos recibidos:', Object.keys(resultado.data));
console.log('logId:', resultado.logId);
