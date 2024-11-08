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
        vShowRes: true, // Disable the resource column.
        vShowComp: false, // Disable the completion column.
        vShowDur: false, // Disable the duration column, because jsgantt doesn't calculate durations the way we want.
        vAdditionalHeaders: {ifcduration: {title: 'Duration'}, "resourceUsage": {title: 'Resource Usage'}},
        vUseToolTip: true, // Disable tooltips.
        vTooltipTemplate: generateTooltip,
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

function generateTooltip(task) {
    var dataObject = task.getDataObject();
    var numberResources = dataObject.resourceUsage ? dataObject.resourceUsage : "NULL"; ;
    return `
    <dl>
        <dt>Name:</dt><dd>{{pName}}</dd>
        <dt>Start:</dt><dd>{{pStart}}</dd>
        <dt>End:</dt><dd>{{pEnd}}</dd>
        <dt>Duration:</dt><dd>${dataObject.ifcduration}</dd>
        <dt>Number of Resources:</dt><dd>${numberResources}</dd>
        <dt>Resources:</dt><dd>{{pRes}}</dd>
    </dl>
    `;
}

function draw_table(json_object){
    let table = document.createElement("table");
    table.classList.add("table-description");
    for (let key in json_object){
        let row = document.createElement("tr");
        let key_cell = document.createElement("td");
        let key_text = document.createTextNode(key);
        key_cell.appendChild(key_text);
        row.appendChild(key_cell);
        let value_cell = document.createElement("td");
        let value_text = document.createTextNode(json_object[key]);
        value_cell.appendChild(value_text);
        row.appendChild(value_cell);
        table.appendChild(row);
    }
    return table;
}

function setupPage(workScheduleData){
    workScheduleData = JSON.parse(workScheduleData);
    let print_button = document.createElement("button");
    print_button.id = "print-schedule";
    print_button.innerHTML = "Print";
    print_button.addEventListener("click", function(){
        g.setTotalHeight("");
        g.Draw();
        var values = document.getElementById("print_page_size").value.split(",")
        let css = 
            "@media print {\n        @page {\n          size: " + values[0] + "mm " + values[1] + "mm;\n        }\n";
        g.printChart(values[0], values[1], css);
        g.setTotalHeight(900);
        g.Draw();
    });
    document.getElementById("print_options").appendChild(print_button);

    let table = draw_table(workScheduleData)
    document.getElementById("schedule-data").appendChild(table);
    table.style.display = "none";
    let toggle_button = document.createElement("button");
    toggle_button.id = "toggle-table";
    toggle_button.innerHTML = "Show Schedule Information";
    toggle_button.onclick = function(){
        if (table.style.display === "none"){
            table.style.display = "table";
            toggle_button.innerHTML = "Hide Schedule Information";
        } else {
            toggle_button.innerHTML = "Show Schedule Information";
            table.style.display = "none";
        }
    }
    document.getElementById("options").appendChild(toggle_button);

    let schedule_name = document.createElement("h2");
    let schedule_name_string = document.createTextNode("Schedule: " + workScheduleData.Name);
    schedule_name.appendChild(schedule_name_string);
    document.getElementById("schedule-header").appendChild(schedule_name);

    let creation_date = document.createElement("h2");
    let creation_date_string = document.createTextNode("Created: " + new Date(workScheduleData.CreationDate).toLocaleDateString());
    creation_date.appendChild(creation_date_string);
    document.getElementById("schedule-header").appendChild(creation_date);
}