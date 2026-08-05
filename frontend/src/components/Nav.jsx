import React from 'react';
import { playSound } from '../audio/audioManager';

function Nav({ active, onClick, children }) {
  return (
    <button
      className={'nav ' + (active ? 'active' : '')}
      onClick={onClick}
      onMouseEnter={() => playSound('click')}
    >
      {children}
    </button>
  );
}

export default Nav;