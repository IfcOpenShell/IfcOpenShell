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
