import { CostUI } from './utilities/costui.js';

const connectedClients = {};
let socket;

$(document).ready(function () {
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

  connectSocket();
  CostUI.createColorPicker();
});

function connectSocket() {
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  socket = io(url);

  socket.on("blender_connect", handleBlenderConnect);
  socket.on("blender_disconnect", handleBlenderDisconnect);
  socket.on("connected_clients", handleConnectedClients);
  socket.on("theme_data", handleThemeData);
  socket.on("connect", handleWebConnect);
  socket.on("cost_schedules", handleCostSchedulesData);
  socket.on("cost_items", handleCostItemsData);
}

function handleBlenderConnect(blenderId) {
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = { shown: false, ifc_file: "" };
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) + 1;
  });
}

function handleBlenderDisconnect(blenderId) {
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeTableElement(blenderId);
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) - 1;
  });
}



function handleConnectedClients(data) {
  $("#blender-count").text(data.length);

  data.forEach(function (id) {
    connectedClients[id] = { shown: false, ifc_file: "" };
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

  var styleElement = $("#index-stylesheet")[0];
  if (styleElement) {
    var sheet = styleElement.sheet || styleElement.styleSheet;
    sheet.insertRule(cssRule, sheet.cssRules.length);
  }
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

function addCostItem(costItemId) {
  console.log("addCostItem", costItemId);
  executeOperator({ type: "addCostItem", costItemId: costItemId });
}

function editCostItemName(costItemId, name) {
  executeOperator({ type: "editCostItemName", costItemId: costItemId, name: name });
}

function selectAssignedElements(costItemId) {
  executeOperator({ type: "selectAssignedElements", costItemId: costItemId });
}

function handleWebConnect() {
  getCostSchedules();
}

function handleCostSchedulesData(data) {
  const blenderId = data.blenderId;
  const costSchedules = data.data["cost_schedules"]["cost_schedules"];
  const currency = data.data["cost_schedules"]["currency"]["name"];

  console.log(data.data["cost_schedules"]);

  const costScheduleDiv = $("#cost-schedules");

  costSchedules.forEach((costSchedule) => {
    costSchedule.UpdateDate = new Date(costSchedule.UpdateDate);
    const mainContainer = CostUI.text("Updated On: " + costSchedule.UpdateDate);
    const callback = () => loadCostSchedule(costSchedule.id, blenderId);


    const card = CostUI.createCard(costSchedule.Name, mainContainer, callback);
    costScheduleDiv.append(card);
  });
}

function handleCostItemsData(data) {
  console.log(data);
  CostUI.createCostSchedule({
    data: data.data["cost_items"],
    blenderID: data.blenderId,
    callbacks: {
      "addCostItem": addCostItem,
      "selectAssignedElements": selectAssignedElements,
      'editCostItemName': editCostItemName,
    }
  });
}

function executeOperator(operator, blenderId) {
  const msg = {
    sourcePage: "cost",
    operator: operator,
  };
  if (blenderId !== undefined) {
    msg.BlenderId = blenderId;
  }
  socket.emit("web_operator", msg);
}

function loadCostSchedule(costScheduleId, blenderId) {
  executeOperator({ type: "loadCostSchedule", costScheduleId: costScheduleId }, blenderId);
}

function getCostSchedules(blenderId) {
  executeOperator({ type: "getCostSchedules" }, blenderId);
}
