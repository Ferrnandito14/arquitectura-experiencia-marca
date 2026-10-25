import React from 'react';
import {Composition} from 'remotion';
import {HamsterReel} from './HamsterReel';
import tiempos from './tiempos.json';

export const RemotionRoot: React.FC = () => (
  <Composition id="HamsterReel" component={HamsterReel} durationInFrames={Math.ceil(tiempos.duracion * 30)} fps={30} width={1080} height={1920} />
);
