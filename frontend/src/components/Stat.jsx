import React from 'react';

function Stat({ title, value, detail }) {
    return (
        <div className="stat">
            <span>{title}</span>
            <strong>{value}</strong>
            <small>{detail}</small>
        </div>
    );
}
