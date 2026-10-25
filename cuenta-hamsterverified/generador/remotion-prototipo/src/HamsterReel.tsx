import React from 'react';
import {AbsoluteFill, Audio, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {useAudioData, visualizeAudio} from '@remotion/media-utils';
import {loadFont} from '@remotion/google-fonts/Inter';
import tiempos from './tiempos.json';

const {fontFamily} = loadFont('normal', {weights: ['500', '700', '800', '900'], subsets: ['latin', 'latin-ext']});

// Colores de la cuenta (los mismos de generar.py)
const PAPEL = '#FFF4E0';
const TINTA = '#2B1D16';
const TEXTO = '#5A4437';
const KICKER = '#A9500E';
const PIE = '#6B5444';

// Zona segura de reels: Instagram tapa ~250 px arriba y ~500 px abajo
const TOP = 250;
const BOTTOM = 500;

const f = (s: number, fps: number) => Math.round(s * fps);

const Palabras: React.FC<{texto: string; desde: number; hasta: number; destacar?: string[]; estilo: React.CSSProperties}> = ({texto, desde, hasta, destacar = [], estilo}) => {
  const frame = useCurrentFrame();
  const palabras = texto.split(' ');
  const paso = Math.max(2, (hasta - desde) / palabras.length);
  return (
    <div style={estilo}>
      {palabras.map((p, i) => {
        const g = frame - desde - i * paso;
        const o = interpolate(g, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const y = interpolate(g, [0, 9], [26, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic)});
        const limpia = p.replace(/[.,¿?]/g, '');
        return (
          <span key={i} style={{display: 'inline-block', opacity: o, transform: `translateY(${y}px)`, marginRight: '0.24em', color: destacar.includes(limpia) ? KICKER : undefined}}>
            {p}
          </span>
        );
      })}
    </div>
  );
};

// El hámster de la cuenta, con la boca que se abre según el volumen de la voz
const Hamster: React.FC<{size: number; boca: number}> = ({size, boca}) => (
  <svg viewBox="0 0 400 400" width={size} height={size}>
    <ellipse cx="200" cy="360" rx="120" ry="14" fill="#3B2A20" opacity=".12" />
    <circle cx="112" cy="118" r="44" fill="#E3A862" /><circle cx="112" cy="118" r="26" fill="#F4B9B0" />
    <circle cx="288" cy="118" r="44" fill="#E3A862" /><circle cx="288" cy="118" r="26" fill="#F4B9B0" />
    <ellipse cx="200" cy="228" rx="150" ry="128" fill="#EDB873" />
    <ellipse cx="200" cy="268" rx="104" ry="84" fill="#FFF1D6" />
    <circle cx="140" cy="212" r="12" fill="#2B1D16" /><circle cx="260" cy="212" r="12" fill="#2B1D16" />
    <circle cx="144" cy="208" r="4" fill="#fff" /><circle cx="264" cy="208" r="4" fill="#fff" />
    <ellipse cx="102" cy="250" rx="26" ry="18" fill="#F4A9A0" opacity=".75" />
    <ellipse cx="298" cy="250" rx="26" ry="18" fill="#F4A9A0" opacity=".75" />
    <ellipse cx="200" cy="238" rx="13" ry="9" fill="#C2675F" />
    <path d="M200 247 v8" stroke="#2B1D16" strokeWidth="5" strokeLinecap="round" />
    {boca > 0.08 ? (
      <ellipse cx="200" cy={268 + boca * 6} rx={16 + boca * 6} ry={4 + boca * 16} fill="#5A2A22" stroke="#2B1D16" strokeWidth="4" />
    ) : (
      <path d="M178 264 q22 14 44 0" stroke="#2B1D16" strokeWidth="5" fill="none" strokeLinecap="round" />
    )}
    <g transform="translate(292 296)"><circle r="40" fill="#1D9BF0" /><path d="M-18 2 l12 13 l25 -28" stroke="#fff" strokeWidth="10" fill="none" strokeLinecap="round" strokeLinejoin="round" /></g>
  </svg>
);

const Globo: React.FC<{texto: string; visible: number}> = ({texto, visible}) => (
  <div style={{position: 'absolute', left: 90, bottom: 600, maxWidth: 600, background: '#fff', border: `4px solid ${TINTA}`, borderRadius: 34, padding: '22px 30px', fontSize: 46, fontWeight: 700, lineHeight: 1.2, color: TINTA, opacity: visible, transform: `scale(${0.85 + visible * 0.15})`, transformOrigin: 'bottom left'}}>
    {texto}
    <div style={{position: 'absolute', right: -22, bottom: 26, width: 0, height: 0, borderTop: '18px solid transparent', borderBottom: '18px solid transparent', borderLeft: `26px solid ${TINTA}`}} />
  </div>
);

export const HamsterReel: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fr = tiempos.frases.map((x) => ({desde: f(x.inicio, fps), hasta: f(x.fin, fps)}));

  // Volumen de la voz en este fotograma, para mover la boca
  const audio = useAudioData(staticFile('voz.wav'));
  let boca = 0;
  if (audio) {
    const v = visualizeAudio({fps, frame, audioData: audio, numberOfSamples: 16});
    boca = Math.min(1, (v.slice(0, 8).reduce((a, b) => a + b, 0) / 8) * 9);
  }

  const entra = spring({frame, fps, config: {damping: 12, stiffness: 110}});
  const salida1 = interpolate(frame, [fr[1].hasta, fr[1].hasta + 10], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const escena2 = frame >= fr[2].desde - 4;
  const sello = spring({frame: frame - fr[2].hasta, fps, config: {damping: 11, stiffness: 160, mass: 0.7}});
  const consejo = interpolate(frame, [fr[3].desde, fr[3].desde + 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const globo1 = interpolate(frame, [fr[1].desde - 4, fr[1].desde + 4, fr[1].hasta + 2, fr[1].hasta + 10], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const globo4 = interpolate(frame, [fr[4].desde - 4, fr[4].desde + 4], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const salto = frame >= fr[4].desde ? Math.abs(Math.sin((frame - fr[4].desde) / 4)) * 14 * Math.max(0, 1 - (frame - fr[4].desde) / 24) : 0;

  return (
    <AbsoluteFill style={{backgroundColor: PAPEL, fontFamily, color: TINTA}}>
      <Audio src={staticFile('musica.wav')} volume={0.16} />
      <Audio src={staticFile('voz.wav')} volume={1} />

      <AbsoluteFill style={{padding: `${TOP}px 90px ${BOTTOM + 220}px 90px`, justifyContent: 'center'}}>
        {!escena2 && (
          <div style={{opacity: salida1}}>
            <Palabras texto="Esencia de un buen correo" desde={0} hasta={12} estilo={{fontSize: 46, fontWeight: 700, color: KICKER, marginBottom: 34}} />
            <Palabras texto="¿Por qué nadie responde tus correos?" desde={fr[0].desde} hasta={fr[0].hasta - 6} destacar={['responde']} estilo={{fontSize: 128, fontWeight: 800, lineHeight: 1.04, letterSpacing: '-0.025em'}} />
          </div>
        )}
        {escena2 && (
          <div>
            {frame >= fr[2].hasta && (
              <div style={{display: 'inline-block', border: '10px solid #1E7B45', color: '#1E7B45', fontSize: 88, fontWeight: 900, letterSpacing: '0.06em', padding: '6px 34px', borderRadius: 14, marginBottom: 56, transform: `rotate(-6deg) scale(${interpolate(sello, [0, 1], [2.4, 1])})`, opacity: Math.min(1, sello * 2)}}>
                ESENCIA
              </div>
            )}
            <Palabras texto="Un correo, una pregunta. Y para cuándo la necesitas." desde={fr[2].desde} hasta={fr[2].hasta - 8} destacar={['una']} estilo={{fontSize: 112, fontWeight: 800, lineHeight: 1.05, letterSpacing: '-0.025em'}} />
            <div style={{fontSize: 52, fontWeight: 500, lineHeight: 1.3, color: TEXTO, marginTop: 40, maxWidth: 600, opacity: consejo}}>
              Si mandas tres preguntas, te van a contestar una.
            </div>
          </div>
        )}
      </AbsoluteFill>

      <Globo texto="Te lo explico en una línea." visible={globo1} />
      <Globo texto="Palabra de hámster." visible={globo4} />

      <div style={{position: 'absolute', right: 50, bottom: 520 + salto, transform: `scale(${entra})`, transformOrigin: 'bottom center'}}>
        <Hamster size={300} boca={boca} />
      </div>

      <div style={{position: 'absolute', left: 90, bottom: 530, fontSize: 34, fontWeight: 700, color: PIE}}>hamsterverified</div>
    </AbsoluteFill>
  );
};
