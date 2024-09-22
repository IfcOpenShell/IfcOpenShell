// keeps track of blenders connected
const connectedClients = {};
const allDrawings = {};
let socket;

// Document ready function
$(document).ready(function () {
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

  $("#dropdown-menu").change(function () {
    const blenderId = $(this).attr("id");
    const ifcFile = $(this).val();
    displayDrawingsNames(blenderId, ifcFile);
  });

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
  socket.on("connect", handleWebConnect);
  socket.on("connected_clients", handleConnectedClients);
  //socket.on("default_data", handleDefaultData);
  socket.on("theme_data", handleThemeData);
  socket.on("drawings_data", handleDrawingsData);
  socket.on("svg_data", handleSvgData);
}

// function used to get drawings data from Bonsai
function handleWebConnect() {
  console.log("Handle Web Connect")
  getDrawingsData();
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  console.log("blender connected: ", blenderId);
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = {
      shown: false,
      ifc_file: "",
      has_drawings: false,
    };
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) + 1;
  });

  const msg = {
    blenderId: blenderId,
    sourcePage: "drawings",
    operator: {
      type: "getDrawings",
    },
  };
  socket.emit("web_operator", msg);
}

// Function to handle 'default_data' event
function handleDefaultData(data) {
  const blenderId = data["blenderId"];
  getDrawingsData(blenderId);
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeSelectOption(blenderId);
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) - 1;
  });
}

function handleConnectedClients(data) {
  $("#blender-count").text(data.length);
  // console.log(data);
  data.forEach(function (id) {
    connectedClients[id] = {
      shown: false,
      ifc_file: "",
      has_drawings: false,
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
  console.log(cssRule);

  var styleElement = $("#drawings-stylesheet")[0];
  if (styleElement) {
    var sheet = styleElement.sheet || styleElement.styleSheet;
    sheet.insertRule(cssRule, sheet.cssRules.length);
  }
}

function handleDrawingsData(data) {
  console.log("Running handleDrawingsData");
  const blenderId = data["blenderId"];

  console.log(data);

  const filename = data["data"]["ifc_file"];
  const drawings = data["data"]["drawings_data"]["drawings"];
  const sheets = data["data"]["drawings_data"]["sheets"];

  allDrawings[filename] = { drawings: drawings, sheets: sheets };

  const hasDrawings = drawings.length > 0 || sheets.length > 0;

  // console.log(connectedClients);

  if (connectedClients.hasOwnProperty(blenderId)) {
    if (!connectedClients[blenderId].shown) {
      connectedClients[blenderId] = {
        shown: true,
        ifc_file: filename,
        has_drawings: hasDrawings,
      };
      addSelectOption(blenderId, filename);
    } else {
      updateSelectOption(blenderId, filename);
    }
  } else {
    connectedClients[blenderId] = {
      shown: true,
      ifc_file: filename,
      has_drawings: hasDrawings,
    };
    addSelectOption(blenderId, filename);
  }
}

function handleSvgData(data) {
  const svgContainer = document.getElementById("svg-container");
  svgContainer.innerHTML = "";
  svgContainer.style.backgroundColor = "white";

  const dom = SVG(svgContainer).svg(data);
  const svgElement = dom.node.children[0];

  // to make the svg not grow outside the svg container
  svgElement.setAttribute("width", "100%");
  svgElement.setAttribute("height", "100%");
  svgElement.style.maxWidth = "100%";
  svgElement.style.maxHeight = "100%";
  svgElement.style.width = "100%";
  svgElement.style.height = "100%";
  svgElement.style.boxSizing = "border-box"; // Ensure padding and borders are included in the element's total width and height

  const panZoomControls = svgPanZoom(svgElement, {
    zoomEnabled: true,
    controlIconsEnabled: true,
    fit: true,
    center: true,
  });
}

function addSelectOption(blenderId, filename) {
  const filenameOption = $("<option></option>")
    .attr("id", "blender-" + blenderId)
    .val(filename)
    .text(filename);
  $("#dropdown-menu").append(filenameOption);
}

function updateSelectOption(blenderId, filename) {
  $("#blender-" + blenderId).text(filename);
  // console.log(blenderId, filename);
  console.log($("#dropdown-menu").val());

  if ($("#dropdown-menu").val() === filename) {
    displayDrawingsNames(blenderId, filename);
  }
}

function removeSelectOption(blenderId) {
  const filename = $("#blender-" + blenderId).val();
  const selectedOption = $("#dropdown-menu").val();

  $("#blender-" + blenderId).remove();
  delete allDrawings[filename];

  if (selectedOption == filename) {
    $("#dropdown-menu").val("0");

    $("#drawings-sub-panel").empty();
    $("#sheets-sub-panel").empty();
  }
}

function displayDrawingsNames(blenderId, ifcFile) {
  drawings = allDrawings[ifcFile].drawings;
  sheets = allDrawings[ifcFile].sheets;

  function createSvgNames(text, index, type) {
    var label = $("<li></lio>")
      .text(text)
      .attr("id", type + "-" + index)
      .addClass("svg-name")
      .click(function () {
        const id = $(this).attr("id").split("-");
        const index = parseInt(id[1]);
        const type = id[0];
        const ifcFile = $("#dropdown-menu").val();

        var path = "";

        if (type === "drawing") {
          path = allDrawings[ifcFile].drawings[index].path;
        } else if (type === "sheet") {
          path = allDrawings[ifcFile].sheets[index].path;
        }

        const msg = {
          path: path,
        };
        // console.log(msg);
        socket.emit("get_svg", msg);

        $("li").removeClass("selected-svg");
        $(this).addClass("selected-svg");
      });

    if (type === "drawing") $("#drawings-sub-panel").append(label);
    else if (type === "sheet") $("#sheets-sub-panel").append(label);
  }

  $("#drawings-sub-panel").empty();
  drawings.forEach(function (drawing, index) {
    createSvgNames(drawing.name, index, "drawing");
  });

  $("#sheets-sub-panel").empty();
  sheets.forEach(function (sheet, index) {
    createSvgNames(sheet.name, index, "sheet");
  });
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
      .text(client.ifc_file || "Blender " + counter);

    clientDiv.append(dropdownIcon);

    const clientDetailsDiv = $("<div>").addClass("client-details");

    if (id) {
      const clientId = $("<div>")
        .addClass("client-detail")
        .text(`Blender ID: ${id}`);
      clientDetailsDiv.append(clientId);
    }

    if (!client.has_drawings) {
      const clientShown = $("<div>")
        .addClass("client-detail")
        .text("No drawings exist for this IFC File yet");
      clientDetailsDiv.append(clientShown);
    } else {
      const clientNumbers = $("<div>")
        .addClass("client-detail")
        .text(
          `${allDrawings[client.ifc_file].drawings.length} Drawing(s), 
          ${allDrawings[client.ifc_file].sheets.length} Sheet(s)`
        );
      clientDetailsDiv.append(clientNumbers);
    }

    clientDiv.append(clientDetailsDiv);

    clientDiv.on("click", function () {
      clientDetailsDiv.toggleClass("show");
    });

    clientList.append(clientDiv);
  });
  clientList.addClass("show");
}

function getDrawingsData(blenderId) {
  const msg = {
    sourcePage: "drawings",
    operator: {
      type: "getDrawings",
    },
  };

  if (blenderId !== undefined) {
    msg.BlenderId = blenderId;
  }

  socket.emit("web_operator", msg);
}
