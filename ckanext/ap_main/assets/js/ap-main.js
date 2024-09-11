ckan.module("ap-main", function ($, _) {
    "use strict";

    return {
        options: {},

        initialize: function () {
            document.querySelector("body").setAttribute("admin-panel-active", true);

            // register plugin helpers inside Sandbox object, available as `this.sandbox`
            // inside every module instance.
            ckan.sandbox.extend({
                "ap": {
                    /**
                     * Transform `{hello_world_prop: 1}` into `{hello:{world:{prop: 1}}}`
                     */
                    nestedOptions(options) {
                        const nested = {};

                        for (let name in options) {
                            if (typeof name !== "string") continue;

                            const path = name.split("_");
                            const prop = path.pop();
                            const target = path.reduce((container, part) => {
                                container[part] = container[part] || {};
                                return container[part];
                            }, nested);
                            target[prop] = options[name];
                        }

                        return nested;
                    },
                },
            });
        }
    };
});
