const SOUND_PATH = "/sounds/";

const SOUNDS = {
    click: "01_soft_click.wav",
    selection: "02_selection.wav",
    menuOpen: "03_menu_open.wav",
    menuClose: "04_menu_close.wav",
    success: "05_success.wav",
    error: "06_error.wav",
    search: "07_search.wav",
    downloadComplete: "08_download_complete.wav",
};

const audioCache = new Map();

function getSound(name) {
    const filename = SOUNDS[name];

    if (!filename) {
        console.warn(`Unknown sound: ${name}`);
        return null;
    }

    if (!audioCache.has(name)) {
        const audio = new Audio(
            `${SOUND_PATH}${filename}`
        );

        audio.preload = "auto";

        audioCache.set(name, audio);
    }

    return audioCache.get(name);
}

export function playSound(name, volume = 1) {
    const sound = getSound(name);

    if (!sound) {
        return;
    }

    sound.pause();
    sound.currentTime = 0;
    sound.volume = Math.max(
        0,
        Math.min(1, volume)
    );

    const playback = sound.play();

    if (playback !== undefined) {
        playback.catch(() => {
            // Browsers can reject playback when audio
            // has not yet been permitted by the user.
        });
    }
}

export function preloadSounds() {
    Object.keys(SOUNDS).forEach((name) => {
        getSound(name);
    });
}

export function isSoundAvailable(name) {
    return Boolean(SOUNDS[name]);
}