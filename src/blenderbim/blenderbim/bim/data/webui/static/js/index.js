$(document).ready(function () {
  // Connect to the Socket.IO server
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  const socket = io(url);
  console.log("socket: ", socket);

  connectedClients = [];

  function addTableElement(blenderId, csvData) {
    const tableDiv = $("<div></div>")
      .addClass("csv-table")
      .attr("id", "table-" + blenderId);
    $("#container").append(tableDiv);

    var table = new Tabulator("#table-" + blenderId, {
      index: "GlobalId",
      data: csvData,
      importFormat: "csv",
      autoColumns: true,
      selectableRows: 1,
      layout: "fitColumns",
      // selectableRowsRangeMode: "click",
    });

    table.on("rowSelected", function (row) {
      var index = row.getIndex(); // the guid of the object
      var tableId = row.getTable().element.id.substr(6);

      msg = JSON.stringify({
        operator_type: "selection",
        blenderId: tableId,
        guid: index,
      });
      socket.emit("operator", msg);
    });
  }

  function updateTableElement(blenderId, csvData) {
    const table = Tabulator.findTable("#table-" + blenderId)[0];
    if (table) {
      table.replaceData(csvData, { importFormat: "csv" });
    }
  }

  function removeTableElement(blenderId) {
    $("#table-" + blenderId).remove();
  }

  socket.on("blender_connect", (blenderId) => {
    console.log("blender_connect: ", blenderId);
    if (!connectedClients.hasOwnProperty(blenderId)) {
      connectedClients[blenderId] = false; // No data shown yet
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
    const csvData = data["data"];
    console.log(data);

    if (connectedClients.hasOwnProperty(blenderId)) {
      if (!connectedClients[blenderId]) {
        addTableElement(blenderId, csvData);
        connectedClients[blenderId] = true; // Data has been shown
      } else {
        updateTableElement(blenderId, csvData);
      }
    } else {
      connectedClients[blenderId] = true;
      addTableElement(blenderId, csvData);
    }
  });
});
