import { CostUI } from './utilities/costui.js';

// keeps track of blenders connected in form of
// shown:bool, workSchedule: {}, ganttTasks: {}, warning: bool
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
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

  connectSocket();
});

// Function to connect to Socket.IO server
function connectSocket() {
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  socket = io(url);

  // Register socket event handlers
  socket.on("blender_connect", handleBlenderConnect);
  socket.on("blender_disconnect", handleBlenderDisconnect);
  socket.on("connected_clients", handleConnectedClients);
  socket.on("connect", handleWebConnect);
  socket.on("theme_data", handleThemeData);
  socket.on("gantt_data", handleGanttData);
  socket.on("default_data", handleDefaultData);
  socket.on("work_schedule_info", handleWorkScheduleData);
}

// function used to get drawings data from Bonsai
function handleWebConnect() {
  getWorkScheduleData();
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = {
      shown: false,
      workSchedule: {},
      ganttTasks: {},
    };
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) + 1;
  });
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeWorkScheduleInfo(blenderId);
    removeGanttElement(blenderId);
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) - 1;
  });
}

function handleConnectedClients(data) {
  $("#blender-count").text(data.length);
  data.forEach(function (id) {
    connectedClients[id] = {
      shown: false,
      workSchedule: {},
      ganttTasks: {},
    };
  });
}

function handleThemeData(themeData) {
  function arrayToRgbString(arr) {
    const [r, g, b, a] = arr.map((num) => Math.round(num * 255));
    if (a !== undefined) {
      return `rgba(${r}, ${g}, ${b}, ${a})`;
    }
    return `rgb(${r}, ${g}, ${b})`;
  }

  function generateCssVariableRule(theme) {
    let cssVariables = ":root.blender {\n";
    for (const key in theme) {
      const cssVariableName = `--blender-${key.replace(/_/g, "-")}`;
      const cssVariableValue = arrayToRgbString(theme[key]);
      cssVariables += `    ${cssVariableName}: ${cssVariableValue};\n`;
    }
    cssVariables += "}";
    return cssVariables;
  }

  const cssRule = generateCssVariableRule(themeData.theme);

  var styleElement = $("#gantt-stylesheet")[0];
  if (styleElement) {
    var sheet = styleElement.sheet || styleElement.styleSheet;
    sheet.insertRule(cssRule, sheet.cssRules.length);
  }
}

function handleWorkScheduleData(data) {
  const blenderId = data["blenderId"];
  const workSchedulesMainDiv = $("#work_schedules");
  const workSchedulesDiv = $("<div>").attr("id", "work_schedules-" + blenderId);
  workSchedulesMainDiv.append(workSchedulesDiv);

  const workSchedules = data["data"]["work_schedule_info"];

  workSchedules.forEach((workSchedule) => {
    const mainContainer = CostUI.Text(
      "Created On: " + new Date(workSchedule.CreationDate).toLocaleDateString(),
      "fa-solid fa-pen-nib"
    );
    const callback = () => loadWorkSchedule(workSchedule.id);
    const card = CostUI.createCard(workSchedule.id, workSchedule.Name,mainContainer, callback);
    workSchedulesDiv.append(card);
  });
}

function handleGanttData(data) {
  const blenderId = data["blenderId"];

  const filename = data["data"]["ifc_file"];
  const ganttTasks = data["data"]["gantt_data"]["tasks"];
  const ganttWorkSched = data["data"]["gantt_data"]["work_schedule"];

  if (connectedClients.hasOwnProperty(blenderId)) {
    if (!connectedClients[blenderId].shown) {
      connectedClients[blenderId] = {
        shown: true,
        ifc_file: filename,
        ganttTasks: ganttTasks,
        workSchedule: ganttWorkSched,
        warning: false,
      };
      addGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
    } else {
      updateGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
      connectedClients[blenderId].workSchedule = ganttWorkSched;
      connectedClients[blenderId].ganttTasks = ganttTasks;
      connectedClients[blenderId].warning = false;
    }
  } else {
    connectedClients[blenderId] = {
      shown: true,
      ifc_file: filename,
      ganttTasks: ganttTasks,
      workSchedule: ganttWorkSched,
      warning: false,
    };
    addGanttElement(blenderId, ganttTasks, ganttWorkSched, filename);
  }
}

function handleDefaultData(data) {
  const blenderId = data["blenderId"];
  const isDirty = data["data"]["is_dirty"];
  showWarning(blenderId, isDirty);
}

// Function to add a new gantt with data and filename

function addGanttElement(blenderId, tasks, workSched, filename) {
  function createWorkSchedDiv(blenderId, workSched) {
    const workSchedDiv = $("<div></div>").attr("id", "workSched" + blenderId);
    const scheduleTable = $("<table></table>")
      .addClass("no-print table-description")
      .attr("id", "workSchedTable-" + blenderId)
      .hide();

    $.each(workSched, (key, value) => {
      value = value ? value : "null";
      $("<tr></tr>")
        .append($("<td></td>").text(key))
        .append($("<td></td>").text(value))
        .appendTo(scheduleTable);
    });

    const toggleButton = $("<button></button>")
      .text("Show Schedule Info")
      .addClass("btn no-print")
      .on("click", function () {
        scheduleTable.toggle();
        const buttonText = scheduleTable.is(":visible")
          ? "Hide Schedule Info"
          : "Show Schedule Info";
        toggleButton.text(buttonText);
      });

    workSchedDiv.append(toggleButton);
    workSchedDiv.append(scheduleTable);

    return workSchedDiv;
  }

  function createGanttInfoDiv(blenderId, workSched) {
    const ganttInfoDiv = $("<div></div>")
      .addClass("gantt-info")
      .attr("id", "gantt-info-" + blenderId);

    const scheduleName = $("<span></span>").text("Schedule: " + workSched.Name);
    const createdOn = $("<span></span>")
      .text("Created: " + new Date(workSched.CreationDate).toLocaleDateString())
      .css("float", "right");

    ganttInfoDiv.append(scheduleName);
    ganttInfoDiv.append(createdOn);

    return ganttInfoDiv;
  }

  function createGantt(blenderId) {
    const ganttDiv = $("<div></div>")
      .addClass("gantt-chart")
      .attr("id", "gantt-" + blenderId);

    let g = new JSGantt.GanttChart(ganttDiv[0], "week");
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

    JSGantt.addJSONTask(g, tasks);
    g.setEditable(true);

    connectedClients[blenderId]["gantt"] = g;

    return ganttDiv;
  }

  function createPrint(blenderId) {
    const printButton = $("<button>", {
      id: "print-btn-" + blenderId,
      html: "Print",
      class: "btn no-print",
    });

    const printOptions = $("<select>", {
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
      $(".gantt-chart").removeClass("no-print");
      $(".gantt-chart")
        .not("#gantt-" + blenderId)
        .addClass("no-print");

      $(".gantt-info")
        .not("#gantt-info-" + blenderId)
        .addClass("no-print");

      const values = printOptions.val().split(",");

      const g = connectedClients[blenderId]["gantt"];
      g.setEditable(false);
      g.setTotalHeight("");
      g.Draw();

      addEventListener("afterprint", () => g.setEditable(true));

      let css = `@media print {
            @page {
                size: ${values[0]}mm ${values[1]}mm;
            }
            body, p, span, h1, h2, h3, h4, h5, h6, div, a, li, td, th, * {
                color: black !important;
            }
        }`;

      g.printChart(values[0], values[1], css);
      g.setTotalHeight(900);
      g.Draw();
    });

    return { printButton, printOptions };
  }

  const ganttContainer = $("<div></div>")
    .addClass("gantt-container")
    .attr("id", "container-" + blenderId);

  const ganttTitle = $("<h3></h3>")
    .attr("id", "title-" + blenderId)
    .text(filename)
    .addClass("no-print")
    .css("margin-bottom", "0.875rem");

  const workSchedDiv = createWorkSchedDiv(blenderId, workSched);
  const ganttInfoDiv = createGanttInfoDiv(blenderId, workSched);
  const ganttDiv = createGantt(blenderId, tasks);
  const { printButton, printOptions } = createPrint(blenderId);

  ganttContainer.append(ganttTitle);
  ganttContainer.append(workSchedDiv);
  ganttContainer.append(ganttInfoDiv);
  ganttContainer.append(ganttDiv);

  ganttContainer.append(printOptions);
  ganttContainer.append(printButton);

  $("#container").append(ganttContainer);

  // have to  call draw after appening the containers to the DOM
  // otherwise the dependencies will not be displayed properly
  const g = connectedClients[blenderId].gantt;
  g.Draw();
}

// Function to update gantt and filename
function updateGanttElement(blenderId, tasks, workSched, filename) {
  // update work schedule table
  const table = $("#workSchedTable-" + blenderId);
  table.empty();
  $.each(workSched, (key, value) => {
    value = value ? value : "null";
    $("<tr></tr>")
      .append($("<td></td>").text(key))
      .append($("<td></td>").text(value))
      .appendTo(table);
  });

  // update gantt chart with new data
  let g = connectedClients[blenderId]["gantt"];
  g.ClearTasks();
  g.Draw();
  JSGantt.addJSONTask(g, tasks);
  g.Draw();

  $("#title-" + blenderId).text(filename);
}

// Function to remove gantt element
function removeGanttElement(blenderId) {
  $("#container-" + blenderId).remove();
}

function showWarning(blenderId, isDirty) {
  connectedClients[blenderId].warning = true;
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

// Event handlers for editing gantt table data
function editValue(list, task, event, cell, column) {
  // console.log("editValue function called with the following parameters:");
  // console.log("list:", list);
  // console.log("task:", task);
  // console.log("event:", event);
  // console.log("cell:", cell);
  // console.log("column:", column);

  const ganttId = task.getGantt()["vDiv"].id;
  const index = ganttId.indexOf("-") + 1;
  const blenderId = ganttId.substring(index);
  const workSchedId = connectedClients[blenderId].workSchedule.id;

  // update data object reprsenting the task
  const dataObj = task.getDataObject();
  dataObj[column] = event.target.value;
  task.setDataObject(dataObj);

  const msg = {
    sourcePage: "gantt",
    blenderId: blenderId,
    operator: {
      type: "editTask",
      workScheduleId: workSchedId,
      taskId: task.getOriginalID(),
      column: column,
      value: event.target.value,
    },
  };
  socket.emit("web_operator", msg);
}

function setTheme(theme) {
  $("html").removeClass("light dark blender").addClass(theme);
  $(":root").css("color-scheme", theme);
  if (theme === "light") {
    $("#toggle-theme").html('<i class="fas fa-sun"></i>');
  } else if (theme === "dark") {
    $("#toggle-theme").html('<i class="fas fa-moon"></i>');
  } else if (theme === "blender") {
    $("#toggle-theme").html('<i class="fas fa-adjust"></i>');
  }
  localStorage.setItem("theme", theme);
}

function toggleTheme() {
  if ($("html").hasClass("light")) {
    setTheme("dark");
  } else if ($("html").hasClass("dark")) {
    setTheme("blender");
  } else {
    setTheme("light");
  }
}

function toggleClientList() {
  var clientList = $("#client-list");

  if (clientList.hasClass("show")) {
    clientList.removeClass("show");
    return;
  }

  clientList.empty();
  var counter = 0;

  $.each(connectedClients, function (id, client) {
    counter++;
    const dropdownIcon = $("<i>")
      .addClass("fas fa-chevron-down")
      .css("margin-left", "0.5rem");

    const clientDiv = $("<div>")
      .addClass("client")
      .addClass(`client-${id}`)
      .text(client.ifc_file || "Blender " + counter);

    if (client.warning) {
      warningIcon = $("<i>")
        .addClass("fas fa-triangle-exclamation warning")
        .css("margin-left", "0.5rem");
      clientDiv.append(warningIcon);
    }

    clientDiv.append(dropdownIcon);

    const clientDetailsDiv = $("<div>").addClass("client-details");

    if (client.warning) {
      warningIcon = $("<i>").addClass("fa-solid fa-triangle-exclamation");
      const clientWarning = $("<div>")
        .addClass("client-detail warning")
        .text(" Might have outdated data due to recent changes in Blender.");
      clientWarning.prepend(warningIcon);
      clientDetailsDiv.append(clientWarning);
    }

    if (id) {
      const clientId = $("<div>")
        .addClass("client-detail")
        .text(`Blender ID: ${id}`);
      clientDetailsDiv.append(clientId);
    }

    if (!client.shown) {
      const clientShown = $("<div>")
        .addClass("client-detail")
        .text("No work schedule exported for this Blender yet");
      clientDetailsDiv.append(clientShown);
    }

    if (client.workSchedule && client.gantt) {
      const clientScheduleName = $("<div>")
        .addClass("client-detail")
        .text(`Schedule Name: ${client.workSchedule.Name}`);

      const clientScheduleDate = $("<div>")
        .addClass("client-detail")
        .text(
          `Schedule Date: ${new Date(
            client.workSchedule.CreationDate
          ).toLocaleDateString()}`
        );

      const scrollButton = $("<button>")
        .addClass("scroll-button")
        .text("Scroll to Gantt Chart")
        .on("click", function () {
          $("html, body").animate(
            { scrollTop: $("#gantt-" + id).offset().top },
            600
          );
          clientList.removeClass("show");
        });

      clientDetailsDiv.append(clientScheduleName);
      clientDetailsDiv.append(clientScheduleDate);
      clientDetailsDiv.append(scrollButton);
    }

    clientDiv.append(clientDetailsDiv);

    clientDiv.on("click", function () {
      clientDetailsDiv.toggleClass("show");
    });

    clientList.append(clientDiv);
  });

  clientList.addClass("show");
}

function loadWorkSchedule(workScheduleId) {
  const msg = {
    sourcePage: "gantt",
    operator: {
      type: "loadWorkSchedule",
      workScheduleId: workScheduleId,
    },
  };
  socket.emit("web_operator", msg);
}

function removeWorkScheduleInfo(blenderId) {
  $("#work_schedules-"+ blenderId).empty();
}

function getWorkScheduleData(blenderId) {
  const msg = {
    sourcePage: "gantt",
    operator: {
      type: "getWorkSchedules",
    },
  };

  if (blenderId !== undefined) {
    msg.BlenderId = blenderId;
  }

  socket.emit("web_operator", msg);
}
