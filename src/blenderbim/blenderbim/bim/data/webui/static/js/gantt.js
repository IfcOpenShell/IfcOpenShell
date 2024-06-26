// keeps track of blenders connected in form of
// shown:bool, work_sched: {}, task_json: {},
const connectedClients = {};
let socket;

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
  const ganttTasks = data["data"]["tasks"];
  // const ganttWorkSched = data["data"]["schedule"];
  const ganttWorkSched = {};
  const filename = data["data"]["IFC_File"];
  console.log(data);
  console.log(ganttTasks);

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
    // vTooltipTemplate: createTooltip,
    vTotalHeight: 900,
  });
  for (var i = 0; i < tasks.length; i++) {
    g.AddTaskItemObject(tasks[i]);
  }
  g.setEditable(true);
  g.Draw();
}

// Function to update gantt and filename
function updateGanttElement(blenderId, ganttTasks, ganttWorkSched, filename) {}

// Function to remove gantt element
function removeGanttElement(blenderId) {
  $("#container-" + blenderId).remove();
}
