/*
 * WebApp-2 Instance Module Registry
 *
 * This file represents the installed/configured software
 * belonging to this particular WebApp-2 instance.
 *
 * It is NOT part of WebApp-2 core.
 */

const STORAGE_KEY = 'webapp2-instance-modules';

export function loadInstalledModules() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (!saved) {
            return [];
        }

        const parsed = JSON.parse(saved);

        return Array.isArray(parsed)
            ? parsed
            : [];
    } catch {
        return [];
    }
}

export function saveInstalledModules(modules) {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(modules)
    );
}
