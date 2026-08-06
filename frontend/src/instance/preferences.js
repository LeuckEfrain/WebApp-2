/*
 * WebApp-2 Instance Preferences
 *
 * Preferences belong to the individual WebApp-2 instance.
 */

const PREFIX = 'webapp2-instance:';

export function loadPreference(key, fallback = null) {
    const value = localStorage.getItem(
        PREFIX + key
    );

    return value === null
        ? fallback
        : value;
}

export function savePreference(key, value) {
    localStorage.setItem(
        PREFIX + key,
        String(value)
    );
}
