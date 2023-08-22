/**
 * Extends core confirm-action.js to append a submit button to a form on submit
 *
 * @param {Event} e
 */
ckan.module.registry["confirm-action"].prototype._onConfirmSuccess = function (e) {
    if (this.el.attr("type") === "submit") {
        this.el.closest("form").append(
            $('<input>').attr({
                type: 'hidden',
                id: this.el.attr("id"),
                name: this.el.attr("name"),
                value: this.el.val()
            })
        )
    }

    this.performAction();
}
