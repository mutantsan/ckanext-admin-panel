ckan.setSchedule = function (scheduleContainer) {
    const min = $("#job-minute").val();
    const hour = $("#job-hour").val();
    const day = $("#job-day").val();
    const month = $("#job-month").val();
    const week = $("#job-week").val();

    $(scheduleContainer).val(`${min} ${hour} ${day} ${month} ${week}`)
}
