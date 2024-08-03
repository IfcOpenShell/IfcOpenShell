// keeps track of blenders connected in form of
// {shown:bool, filename:string, headers:array}
const connectedClients = {};
let socket;

// Document ready function
$(document).ready(function () {
  var systemTheme = window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
  var defaultTheme = "blender";
  var theme = localStorage.getItem("theme") || defaultTheme;
  setTheme(theme);

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
  socket.on("connected_clients", handleConnectedClients);
  socket.on("theme_data", handleThemeData);
  socket.on("csv_data", handleCsvData);
  socket.on("default_data", handleDefaultData);
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  console.log("blender_connect: ", blenderId);
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = { shown: false, ifc_file: "" };
  }
  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) + 1;
  });
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  console.log("blender_disconnect: ", blenderId);
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
  console.log(data);
  data.forEach(function (id) {
    connectedClients[id] = { shown: false, ifc_file: "" };
  });
}

function handleThemeData(themeData) {
  console.log(themeData);

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

  var styleElement = $("#index-stylesheet")[0];
  if (styleElement) {
    var sheet = styleElement.sheet || styleElement.styleSheet;
    sheet.insertRule(cssRule, sheet.cssRules.length);
  }
}

// Function to handle 'csv_data' event
function handleCsvData(data) {
  const blenderId = data["blenderId"];
  const csvData = data["data"]["csv_data"];
  const filename = data["data"]["ifc_file"];
  console.log(data);

  if (connectedClients.hasOwnProperty(blenderId)) {
    if (!connectedClients[blenderId].shown) {
      connectedClients[blenderId] = {
        shown: true,
        ifc_file: filename,
        headers: [],
      };
      addTableElement(blenderId, csvData, filename);
    } else {
      updateTableElement(blenderId, csvData, filename);
    }
  } else {
    connectedClients[blenderId] = {
      shown: true,
      ifc_file: filename,
      headers: [],
    };
    addTableElement(blenderId, csvData, filename);
  }
}

function handleDefaultData(data) {
  const blenderId = data["blenderId"];
  const isDirty = data["data"]["is_dirty"];
  showWarning(blenderId, isDirty);
  console.log(data);
}

// Function to add a new table with data and filename
function addTableElement(blenderId, csvData, filename) {
  // store headers of the csv data
  const firstLine = csvData.indexOf("\n");
  const csvHeaders = csvData.substring(0, firstLine).split(",");
  connectedClients[blenderId].headers = csvHeaders;

  console.log(connectedClients[blenderId]);
  const tableContainer = $("<div></div>")
    .addClass("table-container")
    .attr("id", "container-" + blenderId);

  const tableTitle = $("<h3></h3>")
    .attr("id", "title-" + blenderId)
    .text(filename)
    .css("margin-bottom", "10px");

  const warning = $("<div></div>")
    .attr("id", "warning-" + blenderId)
    .html(
      "&#9888; Warning: This table may contain outdated data due to recent changes in Blender."
    )
    .addClass("warning");

  const tableDiv = $("<div></div>")
    .addClass("csv-table")
    .attr("id", "table-" + blenderId);

  tableContainer.append(tableTitle);
  tableContainer.append(warning);
  tableContainer.append(tableDiv);
  $("#container").append(tableContainer);

  function createHeaderMenu(definitions) {
    var menu = [];

    for (let column of definitions) {
      // Create text element for checkbox
      if (!column.hasOwnProperty("key")) {
        column.visible = true;
      }
      let checkbox = document.createElement("span");
      checkbox.textContent = column.visible ? "\u2611" : "\u2610"; // ☑ or ☐

      // Build label
      let label = document.createElement("span");
      let title = document.createElement("span");

      title.textContent = " " + column.title;

      label.appendChild(checkbox);
      label.appendChild(title);

      // Create menu item
      menu.push({
        label: label,
        action: function (e) {
          // Prevent menu closing
          e.stopPropagation();

          // Toggle current column visibility
          column.visible = !column.visible;
          console.log(column.title, column.visible);
          // Change menu item checkbox
          if (column.visible) {
            table.showColumn(column.title);
            checkbox.textContent = "\u2611"; // ☑
          } else {
            table.hideColumn(column.title);
            checkbox.textContent = "\u2610"; // ☐
          }
        },
      });
    }

    return menu;
  }

  var table = new Tabulator("#table-" + blenderId, {
    height: "400px",
    resizableColumnGuide: true,
    index: "GlobalId",
    data: csvData,
    importFormat: "csv",
    autoColumns: true,
    selectableRows: 1,
    layout: "fitColumns",
    autoColumnsDefinitions: function (definitions) {
      menu = createHeaderMenu(definitions, table);
      definitions.forEach((column) => {
        column.visible = true;
        column.headerMenu = menu;
      });
      return definitions;
    },
  });

  table.on("rowSelected", function (row) {
    var index = row.getIndex(); // the guid of the object

    if (!index) {
      console.log("No Global ID found");
      return;
    }

    // table id is usually "table-BlenderId" so blender id is always
    // after the first 6 characters
    var tableId = row.getTable().element.id.substr(6);

    const msg = {
      sourcePage: "csv",
      blenderId: tableId,
      operator: {
        type: "selection",
        globalId: index,
      },
    };
    socket.emit("web_operator", msg);
  });
}

// Function to update table and filename
function updateTableElement(blenderId, csvData, filename) {
  // check if the headers are the same
  // if yes, just replace the data
  // else, replace the whole data and column definations
  const firstLine = csvData.indexOf("\n");
  const newHeaders = csvData.substring(0, firstLine).split(",");
  const sameHeaders = compareHeaders(
    connectedClients[blenderId].headers,
    newHeaders
  );

  const table = Tabulator.findTable("#table-" + blenderId)[0];
  if (table) {
    if (sameHeaders) {
      table.replaceData(csvData, { importFormat: "csv" });
    } else {
      table.setData(csvData);
      connectedClients[blenderId].headers = newHeaders;
    }
    $("#title-" + blenderId).text(filename);
    $("#warning-" + blenderId).css("display", "none");
  }
}

// Function to remove table element
function removeTableElement(blenderId) {
  $("#container-" + blenderId).remove();
}

function showWarning(blenderId, isDirty) {
  $("#warning-" + blenderId).css("display", "block");
}

// Utility function to compare two csv header
function compareHeaders(headers1, headers2) {
  if (headers1.length !== headers2.length) {
    return false;
  }
  for (let i = 0; i < headers1.length; i++) {
    if (headers1[i] !== headers2[i]) {
      return false;
    }
  }
  return true;
}

function setTheme(theme) {
  $("html").removeClass("light dark blender").addClass(theme);
  var stylesheet = $("#tabulator-stylesheet");
  if (theme === "light") {
    stylesheet.attr(
      "href",
      "https://unpkg.com/tabulator-tables/dist/css/tabulator_site.min.css"
    );
    $("#toggle-theme").html('<i class="fas fa-sun"></i>');
  } else if (theme === "dark") {
    stylesheet.attr(
      "href",
      "https://unpkg.com/tabulator-tables/dist/css/tabulator_site_dark.min.css"
    );
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

    if (!client.shown) {
      const clientShown = $("<div>")
        .addClass("client-detail")
        .text("No CSV exported for this Blender yet");
      clientDetailsDiv.append(clientShown);
    }

    if (client.headers && client.headers.length) {
      const clientHeaders = $("<div>")
        .addClass("client-detail")
        .text(`Table Headers: ${client.headers.join(", ")}`);

      const scrollButton = $("<button>")
        .addClass("scroll-button")
        .text("Scroll to Table")
        .on("click", function () {
          $("html, body").animate(
            { scrollTop: $("#table-" + id).offset().top },
            600
          );
          clientList.removeClass("show");
        });

      clientDetailsDiv.append(clientHeaders);
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
