// keeps track of blenders connected in form of
// {shown:bool, filename:string, headers:array}
const connectedClients = {};
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
  //   socket.on("blender_connect", handleBlenderConnect);
  //   socket.on("blender_disconnect", handleBlenderDisconnect);
  //   socket.on("csv_data", handleCsvData);
  //   socket.on("default_data", handleDefaultData);
}

function setTheme(theme) {
  var stylesheet = $("#tabulator-stylesheet");
  if (theme === "light") {
    stylesheet.attr(
      "href",
      "https://unpkg.com/tabulator-tables/dist/css/tabulator_site.min.css"
    );
    $("html").removeClass("dark").addClass("light");
    $("#toggle-theme").html('<i class="fas fa-sun"></i>');
  } else {
    stylesheet.attr(
      "href",
      "https://unpkg.com/tabulator-tables/dist/css/tabulator_site_dark.min.css"
    );
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
