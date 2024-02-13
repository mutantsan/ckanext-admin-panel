ckan.module("ap-htmx", function ($) {
    return {
        options: {
            formId: null,
        },
        initialize: function () {
            $.proxyAll(this, /_on/);

            document.addEventListener('htmx:beforeRequest', this._onHTMXbeforeRequest);
            document.addEventListener('htmx:afterSettle', this._onHTMXafterSettle);
        },

        _onHTMXbeforeRequest: function (e) {
            $(e.detail.target).find("[data-module]").unbind()

            for (const [key, _] of Object.entries(ckan.module.instances)) {
                ckan.module.instances[key] = null;
            }
        },

        _onHTMXafterSettle: function (e) {
            const doNotInitialize = []

            $(e.detail.target).find("[data-module]").each(function (_, element) {
                const moduleName = $(element).attr("data-module");

                if (!doNotInitialize.includes(moduleName)) {
                    ckan.module.initializeElement(element);
                }
            })
        }
    };
});
