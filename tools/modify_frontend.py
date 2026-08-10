// tools/build-dom-inspector.mjs

import fs from 'node:fs';
import path from 'node:path';

const frontendRoot = path.resolve(
    'D:/Projects/WebApps/webapp_2/frontend'
);

const viteConfigPath = path.join(
    frontendRoot,
    'vite.config.js'
);

const backupDir = path.join(
    frontendRoot,
    '.webapp2-refactor-backups'
);

const source = fs.readFileSync(
    viteConfigPath,
    'utf8'
);

const registrationPattern =
    /webapp2DomInspector\s*\(\s*\)/g;

const existingRegistrations =
    source.match(registrationPattern) ?? [];

if (existingRegistrations.length > 1) {
    throw new Error(
        [
            'Expected exactly one DOM inspector plugin registration.',
            `Expected: 1`,
            `Found: ${existingRegistrations.length}`,
            '',
            'No changes were made.'
        ].join('\n')
    );
}

if (existingRegistrations.length === 1) {
    console.log(
        'DOM inspector plugin is already registered.'
    );
    process.exit(0);
}

const pluginSource = `
function webapp2DomInspector() {
    const snapshots = new Map();

    return {
        name: 'webapp2-dom-inspector',

        configureServer(server) {
            server.middlewares.use(
                '/__webapp2_dom__',
                (req, res) => {
                    if (req.method !== 'GET') {
                        res.statusCode = 405;
                        res.end('Method Not Allowed');
                        return;
                    }

                    const requestUrl = new URL(
                        req.url || '/',
                        'http://localhost'
                    );

                    const requestedPath =
                        requestUrl.searchParams.get(
                            'path'
                        ) || '/';

                    const snapshot =
                        snapshots.get(requestedPath);

                    res.statusCode =
                        snapshot ? 200 : 404;

                    res.setHeader(
                        'Content-Type',
                        snapshot
                            ? 'text/html; charset=utf-8'
                            : 'application/json'
                    );

                    res.setHeader(
                        'Cache-Control',
                        'no-store'
                    );

                    if (snapshot) {
                        res.end(snapshot);
                    } else {
                        res.end(
                            JSON.stringify({
                                error:
                                    'No live DOM snapshot available.',
                                path: requestedPath
                            })
                        );
                    }
                }
            );

            server.middlewares.use(
                '/__webapp2_dom_publish__',
                (req, res) => {
                    if (req.method !== 'POST') {
                        res.statusCode = 405;
                        res.end('Method Not Allowed');
                        return;
                    }

                    let body = '';

                    req.on('data', chunk => {
                        body += chunk;
                    });

                    req.on('end', () => {
                        try {
                            const payload =
                                JSON.parse(body);

                            if (
                                typeof payload.path !==
                                    'string' ||
                                typeof payload.html !==
                                    'string'
                            ) {
                                throw new Error(
                                    'Invalid DOM snapshot.'
                                );
                            }

                            snapshots.set(
                                payload.path,
                                payload.html
                            );

                            res.statusCode = 204;
                            res.end();
                        } catch (error) {
                            res.statusCode = 400;
                            res.setHeader(
                                'Content-Type',
                                'application/json'
                            );

                            res.end(
                                JSON.stringify({
                                    error:
                                        error.message
                                })
                            );
                        }
                    });
                }
            );
        },

        transformIndexHtml(html) {
            const inspector = \`
<script>
(() => {
    if (
        window.__WEBAPP2_DOM_INSPECTOR__
    ) {
        return;
    }

    window.__WEBAPP2_DOM_INSPECTOR__ = true;

    let publishQueued = false;

    async function publishDom() {
        publishQueued = false;

        try {
            await fetch(
                '/__webapp2_dom_publish__',
                {
                    method: 'POST',
                    headers: {
                        'Content-Type':
                            'application/json'
                    },
                    body: JSON.stringify({
                        path:
                            window.location.pathname +
                            window.location.search,
                        html:
                            document.documentElement
                                .outerHTML
                    })
                }
            );
        } catch (_) {
            // Inspection must never
            // interfere with the app.
        }
    }

    function queuePublish() {
        if (publishQueued) {
            return;
        }

        publishQueued = true;

        requestAnimationFrame(
            publishDom
        );
    }

    const observer =
        new MutationObserver(
            queuePublish
        );

    function start() {
        observer.observe(
            document.documentElement,
            {
                subtree: true,
                childList: true,
                attributes: true,
                characterData: true
            }
        );

        queuePublish();
    }

    if (
        document.readyState ===
        'loading'
    ) {
        document.addEventListener(
            'DOMContentLoaded',
            start,
            { once: true }
        );
    } else {
        start();
    }
})();
</script>
\`;

            return html.replace(
                '</head>',
                inspector + '</head>'
            );
        }
    };
}
`;

let modified = source;

/*
 * Insert the plugin implementation before
 * export default defineConfig().
 */
modified = modified.replace(
    /export\s+default\s+defineConfig\s*\(/,
    `${pluginSource}\nexport default defineConfig(`
);

/*
 * Register the plugin inside plugins.
 */
modified = modified.replace(
    /plugins\s*:\s*\[/,
    match =>
        `${match}\n        webapp2DomInspector(),`
);

/*
 * Validate before touching the file.
 */
const finalRegistrations =
    modified.match(registrationPattern) ?? [];

if (finalRegistrations.length !== 1) {
    throw new Error(
        [
            'Expected exactly one DOM inspector plugin registration.',
            `Expected: 1`,
            `Found: ${finalRegistrations.length}`,
            '',
            'No changes were made.'
        ].join('\n')
    );
}

if (
    !modified.includes(
        '/__webapp2_dom__'
    )
) {
    throw new Error(
        'DOM inspection endpoint was not generated.\\n\\nNo changes were made.'
    );
}

if (
    !modified.includes(
        'document.documentElement.outerHTML'
    )
) {
    throw new Error(
        'Live DOM capture was not generated.\\n\\nNo changes were made.'
    );
}

/*
 * Backup only after validation succeeds.
 */
fs.mkdirSync(
    backupDir,
    { recursive: true }
);

const timestamp =
    new Date()
        .toISOString()
        .replace(/[:.]/g, '-');

const backupPath = path.join(
    backupDir,
    `vite.config.js.pre-dom-inspector-${timestamp}`
);

fs.copyFileSync(
    viteConfigPath,
    backupPath
);

fs.writeFileSync(
    viteConfigPath,
    modified,
    'utf8'
);

console.log(
    'DOM inspection build applied successfully.'
);

console.log(
    `Modified: ${viteConfigPath}`
);

console.log(
    `Backup:   ${backupPath}`
);

console.log(
    'Endpoint: /__webapp2_dom__'
);