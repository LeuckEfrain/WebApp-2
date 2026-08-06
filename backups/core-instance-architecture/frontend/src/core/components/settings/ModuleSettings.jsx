function ModuleSettings({
    modules,
    setModules
}) {

    const renameModule = (
        id,
        name
    ) => {

        setModules(current =>
            current.map(module =>
                module.id === id
                    ? {
                        ...module,
                        name
                    }
                    : module
            )
        );

    };


    const toggleModule = (id) => {

        setModules(current =>
            current.map(module =>
                module.id === id
                    ? {
                        ...module,
                        enabled: !module.enabled
                    }
                    : module
            )
        );

    };


    const addModule = () => {

        const id =
            `module-${Date.now()}`;


        const newModule = {

            id,

            name:
                'New Module',

            icon:
                '+',

            enabled:
                true

        };


        setModules(current => [
            ...current,
            newModule
        ]);

    };


    return (
        <section className="module-settings">

            <div className="settings-section-header">

                <div>

                    <div className="eyebrow">
                        HOME
                    </div>

                    <h2>
                        Home Modules
                    </h2>

                </div>


                <p>
                    Rename the applications displayed
                    on the Home screen.
                </p>

            </div>


            <div className="module-settings-list">

                {modules.map(module => (

                    <div
                        className="module-setting"
                        key={module.id}
                    >

                        <div className="module-setting-icon">
                            {module.icon}
                        </div>


                        <div className="module-setting-info">

                            <div className="module-setting-id">
                                {module.id}
                            </div>


                            <label>

                                DISPLAY NAME

                                <input
                                    type="text"
                                    value={module.name}
                                    onChange={event =>
                                        renameModule(
                                            module.id,
                                            event.target.value
                                        )
                                    }
                                />

                            </label>


                            <label className="module-enabled">

                                <input
                                    type="checkbox"
                                    checked={module.enabled}
                                    onChange={() =>
                                        toggleModule(
                                            module.id
                                        )
                                    }
                                />

                                SHOW ON HOME

                            </label>

                        </div>

                    </div>

                ))}

            </div>


            <button
                type="button"
                className="add-module-button"
                onClick={addModule}
            >
                + Add Module
            </button>

        </section>
    );
}


export default ModuleSettings;
