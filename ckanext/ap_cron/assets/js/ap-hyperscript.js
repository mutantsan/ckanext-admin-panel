ckan.setCreateSchedule = function (scheduleContainer) {
    $(scheduleContainer).val(getSchedule("create"))
}

ckan.setEditSchedule = function (scheduleContainer) {
    $(scheduleContainer).val(getSchedule("edit"))
}

/**
 * Get a cron schedule string
 *
 * @returns
 */
function getSchedule(scope) {
    const min = $(`#${scope}-job-minute`).val() || "*";
    const hour = $(`#${scope}-job-hour`).val() || "*";
    const day = $(`#${scope}-job-day`).val() || "*";
    const month = $(`#${scope}-job-month`).val() || "*";
    const week = $(`#${scope}-job-week`).val() || "*";

    return `${min} ${hour} ${day} ${month} ${week}`
}
