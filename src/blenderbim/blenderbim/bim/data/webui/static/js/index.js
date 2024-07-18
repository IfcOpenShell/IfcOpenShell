// keeps track of blenders connected in form of
// {shown:bool, filename:string, headers:array}
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
  socket.on("csv_data", handleCsvData);
  socket.on("default_data", handleDefaultData);
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  console.log("blender_connect: ", blenderId);
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = { shown: false, ifc_file: "" };
  }
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  console.log("blender_disconnect: ", blenderId);
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    removeTableElement(blenderId);
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
