import React from 'react';
import { playSound } from '../audio/audioManager';

function Nav({ active, onClick, children }) {
    return (
        <button
            className={'nav ' + (active ? 'active' : '')}
            onClick={() => {
                playSound('click');
                onClick();
            }}
        >
            {children}
        </button>
    );
}

export default Nav;