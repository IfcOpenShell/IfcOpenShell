let g;

function create_gantt_chart(json_data) {
    g = new JSGantt.GanttChart(document.getElementById('GanttChartDIV'), 'week');
    g.setOptions({
        vCaptionType: 'Caption',  // Set to Show Caption : None,Caption,Resource,Duration,Complete,
        vQuarterColWidth: 36,
        vDateTaskDisplayFormat: 'day dd month yyyy', // Shown in tool tip box
        vDayMajorDateDisplayFormat: 'mon yyyy - Week ww',// Set format to dates in the "Major" header of the "Day" view
        vWeekMinorDateDisplayFormat: 'dd mon', // Set format to display dates in the "Minor" header of the "Week" view
        vLang: "en",
        vShowTaskInfoLink: 1, // Show link in tool tip (0/1)
        vShowEndWeekDate: 0,  // Show/Hide the date for the last day of the week in header for daily
        vUseSingleCell: 10000, // Set the threshold cell per table row (Helps performance for large data.
        vFormatArr: ['Day', 'Week', 'Month', 'Quarter'], // Even with setUseSingleCell using Hour format on such a large chart can cause issues in some browsers,
        vShowRes: false, // Disable the resource column.
        vShowComp: false, // Disable the completion column.
        vShowDur: false, // Disable the duration column, because jsgantt doesn't calculate durations the way we want.
        vAdditionalHeaders: {ifcduration: {title: 'Duration'}},
        vUseToolTip: false, // Disable tooltips.
        vTotalHeight: 900,
    });
    JSGantt.parseJSONString(json_data, g);
    g.Draw();
}
function set_language(e){
    lang = e && e.target ? e.target.value : "en";
    g.setOptions({
        vLang: lang,
    });
    g.Draw();
}

function setupPage(name){
    let print_button = document.createElement("button");
    print_button.id = "print-schedule";
    print_button.innerHTML = "Print";
    print_button.addEventListener("click", function(){
        g.setTotalHeight("");
        g.Draw();
        var values = document.getElementById("print_page_size").value.split(",")
        let css = 
            "@media print {\n        @page {\n          size: " + values[0] + "mm " + values[1] + "mm;\n        }\n        /* set gantt container to the same width as the page */\n        .gantt {\n            width: " + values[0] + "mm;\n        }\n    };";
        g.printChart(values[0], values[1], css);
        g.setTotalHeight(900);
        g.Draw();
    });
    document.getElementById("print_options").appendChild(print_button);

    // add a nice layout to show the schedule name
    let schedule_name = document.createElement("h1");
    // create string to say "Schedule: <name>"
    let schedule_name_string = document.createTextNode("Schedule: " + name);
    // add the string to the h1 element
    schedule_name.appendChild(schedule_name_string);
    document.getElementById("schedule-data").appendChild(schedule_name);
}