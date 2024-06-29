// keeps track of blenders connected in form of
// shown:bool, work_sched: {}, task_json: {},
const connectedClients = {};
let socket;

// print options
const pageSizes = [
  { value: "210,297", text: "A4 Portrait" },
  { value: "297,210", text: "A4 Landscape" },
  { value: "297,420", text: "A3 Portrait" },
  { value: "420,297", text: "A3 Landscape" },
  { value: "420,594", text: "A2 Portrait" },
  { value: "594,420", text: "A2 Landscape" },
  { value: "594,841", text: "A1 Portrait" },
  { value: "841,594", text: "A1 Landscape" },
  { value: "841,1189", text: "A0 Portrait" },
  { value: "1189,841", text: "A0 Landscape" },
];

// Document ready function
$(document).ready(function () {
  connectSocket();
});

// Function to connect to Socket.IO server
function connectSocket() {
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  socket = io(url);
  console.log("socket: ", socket);

  // Register socket event handlers
  socket.on("blender_connect", handleBlenderConnect);
  socket.on("blender_disconnect", handleBlenderDisconnect);
  socket.on("gantt_data", handleGanttData);
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  console.log("blender_connect: ", blenderId);
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = {
      shown: false,
      work_sched: {},
      task_json: {},
    };
  }
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  console.log("blender_disconnect: ", blenderId);
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeGanttElement(blenderId);
  }
}

// Function to handle 'gantt_data' event
function handleGanttData(data) {
  const blenderId = data["blenderId"];

  console.log(data);

  const filename = data["data"]["IFC_File"];
  const ganttTasks = data["data"]["gantt_data"]["tasks"];
  // const ganttWorkSched = data["data"]["gantt_data"]["work_schedule"];
  const ganttWorkSched = {};

  if (connectedClients.hasOwnProperty(blenderId)) {
    if (!connectedClients[blenderId].shown) {
      connectedClients[blenderId] = {
        shown: false,
        work_sched: ganttTasks,
        task_json: ganttWorkSched,
      };
      addGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
    } else {
      updateGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
    }
  } else {
    connectedClients[blenderId] = {
      shown: false,
      work_sched: ganttTasks,
      task_json: ganttWorkSched,
    };
    addGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
  }
}

// Function to add a new gantt with data and filename
function addGanttElement(blenderId, tasks, WorkSched, filename) {
  const ganttContainer = $("<div></div>")
    .addClass("gantt-container")
    .attr("id", "container-" + blenderId);

  const ganttTitle = $("<h3></h3>")
    .attr("id", "title-" + blenderId)
    .text(filename)
    .addClass("no-print")
    .css("margin-bottom", "10px");

  const ganttDiv = $("<div></div>")
    .addClass("gantt-chart")
    .attr("id", "gantt-" + blenderId);

  ganttContainer.append(ganttTitle);
  ganttContainer.append(ganttDiv);
  $("#container").append(ganttContainer);

  let g = new JSGantt.GanttChart($("#gantt-" + blenderId)[0], "week");
  g.setOptions({
    vCaptionType: "Caption", // Set to Show Caption : None,Caption,Resource,Duration,Complete,
    vQuarterColWidth: 36,
    vDateTaskDisplayFormat: "day dd month yyyy", // Shown in tool tip box
    vDayMajorDateDisplayFormat: "mon yyyy - Week ww", // Set format to dates in the "Major" header of the "Day" view
    vWeekMinorDateDisplayFormat: "dd mon", // Set format to display dates in the "Minor" header of the "Week" view
    vLang: "en",
    vShowTaskInfoLink: 1, // Show link in tool tip (0/1)
    vShowEndWeekDate: 0, // Show/Hide the date for the last day of the week in header for daily
    vUseSingleCell: 10000, // Set the threshold cell per table row (Helps performance for large data.
    vFormatArr: ["Day", "Week", "Month", "Quarter"], // Even with setUseSingleCell using Hour format on such a large chart can cause issues in some browsers,
    vShowRes: true, // Disable the resource column.
    vShowComp: false, // Disable the completion column.
    vShowDur: false, // Disable the duration column, because jsgantt doesn't calculate durations the way we want.
    vAdditionalHeaders: {
      ifcduration: { title: "Duration" },
      resourceUsage: { title: "Resource Usage" },
    },
    vUseToolTip: true, // Disable tooltips.
    vTooltipTemplate: generateTooltip,
    vTotalHeight: 900,

    vEventsChange: {
      taskname: editValue, // if you need to use the this scope, do: editValue.bind(this)
      res: editValue,
      dur: editValue,
      comp: editValue,
      start: editValue,
      end: editValue,
      planstart: editValue,
      planend: editValue,
      cost: editValue,
      additional_category: editValue,
    },
  });
  for (var i = 0; i < tasks.length; i++) {
    g.AddTaskItemObject(tasks[i]);
  }
  g.setEditable(true);
  g.Draw();

  let printButton = $("<button>", {
    id: "print-btn-" + blenderId,
    html: "Print",
    class: "no-print",
  });

  let printOptions = $("<select>", {
    id: "print-options-" + blenderId,
    class: "no-print",
  });

  $.each(pageSizes, function (index, size) {
    printOptions.append(
      $("<option>", {
        value: size.value,
        text: size.text,
      })
    );
  });

  printButton.on("click", function () {
    // make it only the corresponding gantt chart is printed
    $(".gantt-chart").removeClass("no-print");
    $(".gantt-chart")
      .not("#gantt-" + blenderId)
      .addClass("your-css-class");

    var values = $("#print-options-" + blenderId)
      .val()
      .split(",");

    g.setEditable(false);
    g.setTotalHeight("");
    g.Draw();

    let css =
      "@media print {\n" +
      "    @page {\n" +
      "        size: " +
      values[0] +
      "mm " +
      values[1] +
      "mm;\n" +
      "    }\n" +
      "    /* Make all text black */\n" +
      "    body, p, span, h1, h2, h3, h4, h5, h6, div, a, li, td, th, * {\n" +
      "        color: black !important;\n" +
      "    }\n" +
      "}";
    g.printChart(values[0], values[1], css);
    g.setTotalHeight(900);
    g.Draw();
  });
  ganttContainer.append(printOptions);
  ganttContainer.append(printButton);
}

// Function to update gantt and filename
function updateGanttElement(blenderId, ganttTasks, ganttWorkSched, filename) {}

// Function to remove gantt element
function removeGanttElement(blenderId) {
  $("#container-" + blenderId).remove();
}

// Utility function to create a tooltip for the gantt chars
function generateTooltip(task) {
  var dataObject = task.getDataObject();
  var numberResources = dataObject.resourceUsage
    ? dataObject.resourceUsage
    : "NULL";
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

function editValue(list, task, event, cell, column) {
  console.log("editValue function called with the following parameters:");
  console.log("list:", list);
  console.log("task:", task);
  console.log("event:", event);
  console.log("cell:", cell);
  console.log("column:", column);

  const blenderId = task.getGantt()["vDiv"].id.split("-")[1];

  // update data object reprsenting the task
  const dataObj = task.getDataObject();
  dataObj[column] = event.target.value;
  task.setDataObject(dataObj);

  const msg = {
    sourcePage: "gantt",
    blenderId: blenderId,
    operator: {
      type: "editTask",
      column: column,
      value: event.target.value,
    },
  };
  // socket.emit("web_operator", msg);
}
