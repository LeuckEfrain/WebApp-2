const CONTINUITY_ENDPOINT =
    '/__webapp2_continuity__';


const SECTION_DEFINITIONS = [
    {
        id: 'vision',
        title: 'Project Vision',
        sourceSections: [
            'PROJECT_VISION',
            'CORE_HOME-SCREEN_CONCEPT',
            'DESIGN_PHILOSOPHY'
        ]
    },
    {
        id: 'protocols',
        title: 'Protocols',
        sourceSections: [
            'MODULARIZATION_PROTOCOL__VERY_IMPORTANT',
            'MODULARIZATION_SCRIPT_PROTOCOL',
            'RESOURCE-USE_PROTOCOL__VERY_IMPORTANT',
            'GIT_/_REPOSITORY_PROTOCOL',
            'BACKUP_PROTOCOL',
            'DEVELOPMENT_WORKFLOW',
            'CURRENT_CODE_ORGANIZATION_PRINCIPLE',
            'AUTOMATED_CONTINUITY-UPDATE_PROTOCOL',
            'PER-CHANGE_REVISION_RECORD_PROTOCOL',
            'DEDICATED_BACKUP_DIRECTORY',
            'CONTINUITY VERSION TRACKER'
        ]
    },
    {
        id: 'goals',
        title: 'Goals',
        sourceSections: [
            'CURRENT_IMMEDIATE_PRIORITY',
            'GOAL LIFECYCLE AND COMPLETION PROTOCOL',
            'THINGS_NOT_TO_FORGET'
        ]
    },
    {
        id: 'architecture',
        title: 'Architecture',
        sourceSections: [
            'CURRENT_IMPLEMENTED_ARCHITECTURE',
            'CURRENT_MODULE_SYSTEM',
            'INSTANCE-LOCAL MODULE ARCHITECTURE'
        ]
    },
    {
        id: 'phases',
        title: 'Development Phases',
        sourceSections: [
            'CURRENT_DESIGN_PHASE',
            'PHASE_ROADMAP'
        ]
    }
];


function normalize(value) {
    return value
        .trim()
        .replace(/^#{1,6}\s*/, '')
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .toUpperCase();
}


function isDelimiter(line) {
    return (
        !line ||
        /^={3,}$/.test(line) ||
        /^-{3,}$/.test(line)
    );
}


function isHeading(line) {
    const value = line.trim();

    if (!value || isDelimiter(value)) {
        return false;
    }

    if (/^#{1,6}\s+/.test(value)) {
        return true;
    }

    return (
        value === value.toUpperCase() &&
        /[A-Z]/.test(value)
    );
}


function cleanHeading(line) {
    return line
        .trim()
        .replace(/^#{1,6}\s*/, '')
        .replace(/\s+/g, ' ')
        .trim();
}


function parseDocument(text) {
    const lines = text
        .replace(/\r\n/g, '\n')
        .split('\n');

    const sections = [];

    let current = null;

    for (const rawLine of lines) {
        const line = rawLine.trim();

        const sectionMatch = line.match(
            /^\[SECTION:\s*(.+?)\s*\]$/
        );

        if (sectionMatch) {
            const title = sectionMatch[1].trim();

            current = {
                title,
                normalizedTitle: normalize(title),
                lines: []
            };

            sections.push(current);
            continue;
        }

        if (/^\[END_SECTION\]$/.test(line)) {
            current = null;
            continue;
        }

        // Ignore document-level content before the first structured section.
        if (!current) {
            continue;
        }

        // The structured continuity document contains a TITLE line
        // immediately inside each section. The section marker already
        // supplies the canonical title, so do not duplicate that line.
        if (
            current.lines.length === 0 &&
            /^TITLE:\s*/i.test(line)
        ) {
            continue;
        }

        // Ignore empty lines while preserving actual section content.
        if (line) {
            current.lines.push(line);
        }
    }

    return sections;
}


function findSections(sections, definition) {
    const accepted = definition.sourceSections.map(normalize);

    return sections.filter(section =>
        accepted.includes(section.normalizedTitle)
    );
}


function lineToItem(line, index) {
    const cleaned = line
        .replace(/^[-*•]\s*/, '')
        .replace(/^\d+[.)]\s*/, '')
        .trim();

    if (!cleaned) {
        return null;
    }

    const separatorIndex = cleaned.indexOf(':');

    if (
        separatorIndex > 0 &&
        separatorIndex < 80
    ) {
        const title = cleaned
            .slice(0, separatorIndex)
            .trim();

        const body = cleaned
            .slice(separatorIndex + 1)
            .trim();

        if (title && body) {
            return {
                title,
                body
            };
        }
    }

    return {
        title: `Item ${index + 1}`,
        body: cleaned
    };
}


function buildGoalItems(lines) {
    return lines
        .map((line, index) => lineToItem(line, index))
        .filter(Boolean);
}


function buildSection(documentSections, definition) {
    if (!documentSections.length) {
        return {
            id: definition.id,
            title: definition.title,
            description:
                'This section is not currently present in the authoritative continuity document.',
            content: [],
            items: [],
            goals: [],
            phases: []
        };
    }

    /*
     * Preserve section boundaries instead of flattening every source line
     * immediately. This is important because the continuity document contains
     * several distinct authoritative sections that belong to one viewer tab.
     */
    const content = [];

    for (const source of documentSections) {
        if (content.length > 0) {
            content.push('');
        }

        content.push(
            `[${source.title}]`
        );

        content.push(...source.lines);
    }

    const result = {
        id: definition.id,
        title: definition.title,
        description:
            'Loaded dynamically from the authoritative continuity document.',
        content,
        items: [],
        goals: [],
        phases: []
    };

    if (definition.id === 'goals') {
        result.goals = buildGoalItems(
            documentSections.flatMap(section => section.lines)
        ).map((item, index) => ({
            id: `${definition.id}-${index}`,
            title: item.title,
            status: 'Current',
            body: item.body,
            phases: []
        }));
    } else if (definition.id === 'phases') {
        result.phases = documentSections.flatMap(
            section =>
                section.lines
                    .map((line, index) => ({
                        source: section.title,
                        title: line.startsWith('PHASE ')
                            ? line
                            : `Phase item ${index + 1}`,
                        status: 'Current',
                        body: line
                    }))
                    .filter(item => item.body)
        );
    } else {
        result.items = documentSections.flatMap(section =>
            section.lines
                .map((line, index) => lineToItem(line, index))
                .filter(Boolean)
        );
    }

    return result;
}


function buildViewerSections(text) {
    const sections = parseDocument(text);

    return SECTION_DEFINITIONS.map(definition =>
        buildSection(
            findSections(sections, definition),
            definition
        )
    );
}


export async function loadContinuitySections() {
    const response = await fetch(
        CONTINUITY_ENDPOINT,
        {
            cache: 'no-store'
        }
    );

    if (!response.ok) {
        throw new Error(
            `Continuity endpoint returned HTTP ${response.status}.`
        );
    }

    const text = await response.text();

    return {
        text,
        sections: buildViewerSections(text)
    };
}
