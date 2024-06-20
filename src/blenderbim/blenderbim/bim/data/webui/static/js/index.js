$(document).ready(function () {
  // Connect to the Socket.IO server
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  const socket = io(url);
  console.log("socket: ", socket);

  // keeps track of blenders connected in form of
  // {shown:bool, filename:name}
  const connectedClients = {};

  // add a new talbe with data and filename
  function addTableElement(blenderId, csvData, filename) {
    const tableContainer = $("<div></div>")
      .addClass("table-container")
      .attr("id", "container-" + blenderId);

    const tableTitle = $("<h3></h3>")
      .attr("id", "title-" + blenderId)
      .text(filename)
      .css("margin-bottom", "10px");

    const tableDiv = $("<div></div>")
      .addClass("csv-table")
      .attr("id", "table-" + blenderId);

    tableContainer.append(tableTitle);
    tableContainer.append(tableDiv);
    $("#container").append(tableContainer);

    var table = new Tabulator("#table-" + blenderId, {
      height: "400px",
      index: "GlobalId",
      data: csvData,
      importFormat: "csv",
      autoColumns: true,
      selectableRows: 1,
      layout: "fitColumns",
    });

    table.on("rowSelected", function (row) {
      var index = row.getIndex(); // the guid of the object
      // table id is usually "table-BlenderId" so blender id is always
      // after the first 6 characters
      var tableId = row.getTable().element.id.substr(6);

      const msg = {
        blenderId: tableId,
        operator: {
          type: "selection",
          GlobalId: index,
        },
      };
      socket.emit("web_operator", msg);
    });
  }

  // update table and filename
  function updateTableElement(blenderId, csvData, filename) {
    // TODO: see if we can only replace updated rows only.
    // TODO: and handle case where new columns are added
    // for now just replace the data in the table
    const table = Tabulator.findTable("#table-" + blenderId)[0];
    if (table) {
      table.setData(csvData);
      $("#title-" + blenderId).text(filename); // Update the title
    }
  }

  function removeTableElement(blenderId) {
    $("#container-" + blenderId).remove();
  }

  socket.on("blender_connect", (blenderId) => {
    console.log("blender_connect: ", blenderId);
    if (!connectedClients.hasOwnProperty(blenderId)) {
      connectedClients[blenderId] = { shown: false, ifc_file: "" };
    }
  });

  socket.on("blender_disconnect", (blenderId) => {
    console.log("blender_disconnect: ", blenderId);
    if (connectedClients.hasOwnProperty(blenderId)) {
      delete connectedClients[blenderId];
      removeTableElement(blenderId);
    }
  });

  socket.on("csv_data", (data) => {
    const blenderId = data["blenderId"];
    const csvData = data["data"]["data"];
    const filename = data["data"]["IFC_File"];
    console.log(data);

    if (connectedClients.hasOwnProperty(blenderId)) {
      if (!connectedClients[blenderId].shown) {
        addTableElement(blenderId, csvData, filename);
        connectedClients[blenderId] = { shown: true, ifc_file: filename };
      } else {
        updateTableElement(blenderId, csvData, filename);
      }
    } else {
      connectedClients[blenderId] = { shown: true, ifc_file: filename };
      addTableElement(blenderId, csvData, filename);
    }
  });
});
