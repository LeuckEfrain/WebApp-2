function normalizePackageResults(data, managerId) {
    if (!data) {
        return [];
    }

    // pip already returns structured results.
    if (managerId === 'pip' && Array.isArray(data.results)) {
        return data.results.map(pkg => ({
            name: pkg.name || 'Unknown package',
            package: pkg.name || '',
            description: pkg.description || 'No description available.',
            manager: 'pip',
            source: 'pip'
        }));
    }

    // npm returns JSON through the backend's output field.
    if (managerId === 'npm' && data.output) {
        try {
            const parsed = JSON.parse(data.output);

            if (Array.isArray(parsed)) {
                return parsed.map(pkg => ({
                    name: pkg.name || 'Unknown package',
                    package: pkg.name || '',
                    description: pkg.description || 'No description available.',
                    manager: 'npm',
                    source: 'npm',
                    version: pkg.version || ''
                }));
            }
        } catch {
            return [];
        }
    }

    // WinGet and Chocolatey currently return terminal output.
    if (data.output) {
        return parseCommandLineResults(data.output, managerId);
    }

    return [];
}

function parseCommandLineResults(output, managerId) {
    const lines = output
        .split('\n')
        .map(line => line.trim())
        .filter(Boolean);

    const results = [];

    for (const line of lines) {
        if (
            line.startsWith('Name') ||
            line.startsWith('---') ||
            line.startsWith('Source') ||
            line.startsWith('Chocolatey') ||
            line.startsWith('Microsoft')
        ) {
            continue;
        }

        const parts = line.split(/\s{2,}/);

        if (!parts[0]) {
            continue;
        }

        results.push({
            name: parts[0],
            package: parts[1] || parts[0],
            description: '',
            manager: managerId,
            source: managerId,
            version: parts[2] || ''
        });
    }

    return results;
}

function relevanceScore(result, query) {
    const search = query.trim().toLowerCase();
    const name = (result.name || '').toLowerCase();
    const packageName = (result.package || '').toLowerCase();
    const description = (result.description || '').toLowerCase();

    let score = 0;

    if (name === search) {
        score += 100;
    }

    if (packageName === search) {
        score += 95;
    }

    if (name.startsWith(search)) {
        score += 60;
    }

    if (packageName.startsWith(search)) {
        score += 55;
    }

    if (name.includes(search)) {
        score += 40;
    }

    if (packageName.includes(search)) {
        score += 35;
    }

    if (description.includes(search)) {
        score += 15;
    }

    const words = search
        .split(/\s+/)
        .filter(Boolean);

    for (const word of words) {
        if (name.includes(word)) {
            score += 10;
        }

        if (packageName.includes(word)) {
            score += 8;
        }

        if (description.includes(word)) {
            score += 3;
        }
    }

    return score;
}

function rankPackageResults(results, query) {
    return results
        .map(result => ({
            ...result,
            relevance: relevanceScore(result, query)
        }))
        .sort((a, b) => b.relevance - a.relevance);
}

function determineBestSource(results) {
    if (!results.length) {
        return null;
    }

    const sourceScores = {};

    for (const result of results) {
        if (!sourceScores[result.manager]) {
            sourceScores[result.manager] = {
                manager: result.manager,
                score: 0,
                count: 0
            };
        }

        sourceScores[result.manager].score += result.relevance;
        sourceScores[result.manager].count += 1;
    }

    return Object.values(sourceScores)
        .sort((a, b) => {
            const scoreA = a.score / Math.max(a.count, 1);
            const scoreB = b.score / Math.max(b.count, 1);

            return scoreB - scoreA;
        })[0];
}

export {
    normalizePackageResults,
    parseCommandLineResults,
    relevanceScore,
    rankPackageResults,
    determineBestSource
};
