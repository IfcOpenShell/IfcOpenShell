// keeps track of blenders connected
const connectedClients = {};
const allDrawings = {};
let socket;

// Document ready function
$(document).ready(function () {
  var systemTheme = window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
  var theme = localStorage.getItem("theme") || systemTheme;
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
  socket.on("connect", handleWebConnect);
  socket.on("drawings_data", handleDrawingsData);
  //   socket.on("default_data", handleDefaultData);
}

// function used to get drawings data from blenderbim
function handleWebConnect() {
  const msg = {
    sourcePage: "drawings",
    operator: {
      type: "getDrawings",
    },
  };
  socket.emit("web_operator", msg);
}

// Function to handle 'blender_connect' event
function handleBlenderConnect(blenderId) {
  console.log("blender_connect: ", blenderId);
  if (!connectedClients.hasOwnProperty(blenderId)) {
    connectedClients[blenderId] = {
      shown: false,
      ifc_file: "",
    };
  }
}

// Function to handle 'blender_disconnect' event
function handleBlenderDisconnect(blenderId) {
  console.log("blender_disconnect: ", blenderId);
  if (connectedClients.hasOwnProperty(blenderId)) {
    delete connectedClients[blenderId];
    // remove(blenderId);
  }

  $("#blender-count").text(function (i, text) {
    return parseInt(text, 10) - 1;
  });
}

function handleDrawingsData(data) {
  const blenderId = data["blenderId"];

  console.log(data);

  const filename = data["data"]["ifc_file"];
  const drawings = data["data"]["drawings_data"]["drawings"];
  const sheets = data["data"]["drawings_data"]["sheets"];

  allDrawings[filename] = { drawings: drawings, sheets: sheets };

  if (connectedClients.hasOwnProperty(blenderId)) {
    if (!connectedClients[blenderId].shown) {
      connectedClients[blenderId] = {
        shown: true,
        ifc_file: filename,
      };
      // add(blenderId, data, filename);
    } else {
      // update(blenderId, data, filename);
    }
  } else {
    connectedClients[blenderId] = {
      shown: true,
      ifc_file: filename,
    };
    // add(blenderId, data, filename);
  }
}

function setTheme(theme) {
  if (theme === "light") {
    $("html").removeClass("dark").addClass("light");
    $("#toggle-theme").html('<i class="fas fa-sun"></i>');
  } else {
    $("html").removeClass("light").addClass("dark");
    $("#toggle-theme").html('<i class="fas fa-moon"></i>');
  }
  localStorage.setItem("theme", theme);
}

function toggleTheme() {
  if ($("html").hasClass("dark")) {
    setTheme("light");
  } else {
    setTheme("dark");
  }
}

function toggleClientList() {
  var clientList = $("#client-list");

  if (clientList.hasClass("show")) {
    clientList.removeClass("show");
    return;
  }

  clientList.empty();

  $.each(connectedClients, function (id, client) {
    if (!client.shown) return;

    const dropdownIcon = $("<i>")
      .addClass("fas fa-chevron-down")
      .css("margin-left", "0.5rem");

    const clientDiv = $("<div>").addClass("client").text(client.ifc_file);

    clientDiv.append(dropdownIcon);

    const clientDetailsDiv = $("<div>").addClass("client-details");

    if (id) {
      const clientId = $("<div>")
        .addClass("client-detail")
        .text(`Blender ID: ${id}`);
      clientDetailsDiv.append(clientId);
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
            {
              scrollTop: $("#table-" + id).offset().top,
            },
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
