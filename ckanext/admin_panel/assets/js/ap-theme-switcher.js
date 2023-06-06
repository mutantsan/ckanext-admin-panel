// THEME SWITCHER BUTTON
// switch themes bettwen dark and light
// save current theme in the Local Storage
ckan.module("ap-theme-switcher", function ($, _) {
    "use strict";
    return {
        options: {},

        initialize: function () {
            this.light = "light";
            this.dark = "dark";

            this.defaultSchema = this.light;
            this.buttonsTarget = ".ap-theme-switcher";
            this.localStorageKey = "apPreferredColorScheme";

            this.scheme = this.getSchemeFromLS();

            this.addButton();
            this.initSwitchers();
            this.applyScheme();
        },

        getSchemeFromLS: function () {
            let currentSchema = window.localStorage.getItem(this.localStorageKey);
            return currentSchema ? currentSchema : this.defaultSchema
        },

        saveSchemeToLS: function () {
            window.localStorage.setItem(this.localStorageKey, this.scheme)
        },

        applyScheme: function () {
            document.querySelector("body").setAttribute("admin-panel-theme", this.scheme);
            document.querySelector("#admin-panel").setAttribute("admin-panel-theme", this.scheme);
        },

        addButton: function () {
            let btn = document.createElement("BUTTON");
            btn.className = "ap-theme-switcher";
            btn.title = "Dark theme switcher"
            document.querySelector("#admin-panel .collapse").appendChild(btn)
        },

        initSwitchers: function () {
            document.querySelectorAll(this.buttonsTarget).forEach(e => {
                e.addEventListener("click", () => {
                    this.scheme = this.scheme == this.light ? this.dark : this.light;
                    this.applyScheme();
                    this.saveSchemeToLS();
                });
            }
            );
        },
    };
});
