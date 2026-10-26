import React from 'react';
import {Composition} from 'remotion';
import {HamsterResponde, PropsResponde} from './HamsterResponde';

// Valores de ejemplo; en el render real llegan con --props desde hacer_reel.py
const ejemplo: PropsResponde = {
  serie: 'El hámster responde',
  pregunta: '¿Cómo dejo de postergar?',
  puente: 'Te lo explico en una línea.',
  titular: 'Empieza dos minutos.',
  destacar: ['dos'],
  consejo: 'Casi siempre, seguir cuesta menos que empezar.',
  cierre: 'Palabra de hámster.',
  sello: null,
  tiempos: {duracion: 12, frases: [{inicio: 0.3, fin: 2}, {inicio: 2.3, fin: 3.8}, {inicio: 4.2, fin: 6}, {inicio: 6.4, fin: 9.5}, {inicio: 10, fin: 11}]},
  voz: 'voz.wav',
  musica: 'musica.wav',
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="HamsterResponde"
    component={HamsterResponde}
    fps={30}
    width={1080}
    height={1920}
    durationInFrames={360}
    defaultProps={ejemplo}
    calculateMetadata={({props}) => ({durationInFrames: Math.ceil(props.tiempos.duracion * 30)})}
  />
);
