import { useCallback, useRef } from 'react';

export const useSound = () => {
  const audioContext = useRef(null);
  const soundBuffers = useRef({});

  const initContext = useCallback(() => {
    if (!audioContext.current) {
      audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.current.state === 'suspended') {
      audioContext.current.resume();
    }
  }, []);

  const loadSound = useCallback(async (name, url) => {
    initContext();
    if (soundBuffers.current[name]) return;

    try {
      const response = await fetch(url);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContext.current.decodeAudioData(arrayBuffer);
      soundBuffers.current[name] = audioBuffer;
    } catch (error) {
      console.error(`Failed to load sound: ${name}`, error);
    }
  }, [initContext]);

  const playSound = useCallback((name, volume = 0.5) => {
    if (!audioContext.current || !soundBuffers.current[name]) return;

    const source = audioContext.current.createBufferSource();
    source.buffer = soundBuffers.current[name];

    const gainNode = audioContext.current.createGain();
    gainNode.gain.value = volume;

    source.connect(gainNode);
    gainNode.connect(audioContext.current.destination);

    source.start(0);
  }, []);

  return { loadSound, playSound, initContext };
};
