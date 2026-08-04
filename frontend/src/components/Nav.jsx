import React from 'react';

function Nav({ active, onClick, children }) {
    return (
        <button
            className={'nav ' + (active ? 'active' : '')}
            onClick={onClick}
        >
            {children}
        </button>
    );
}
