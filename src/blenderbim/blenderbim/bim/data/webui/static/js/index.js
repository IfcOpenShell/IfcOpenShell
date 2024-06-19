$(document).ready(function () {
  // Connect to the Socket.IO server
  const url = "ws://localhost:" + SOCKET_PORT + "/web";

  const socket = io(url);

  console.log("socket: ", socket);

  const connectedClients = {};

  function addMessageElement(blenderId, message) {
    const messageDiv = $("<div></div>")
      .addClass("message")
      .attr("id", blenderId)
      .text(message);

    $("#messages").append(messageDiv);
  }

  function updateMessageElement(blenderId, message) {
    $("#" + blenderId).text(message);
  }

  function removeMessageElement(blenderId) {
    $("#" + blenderId).remove();
  }

  socket.on("blender_connect", (blenderId) => {
    console.log("blender_connect: ", blenderId);

    if (!connectedClients[blenderId]) {
      connectedClients[blenderId] = true;
      addMessageElement(blenderId, "");
    }
  });

  // Listen for client disconnect events
  socket.on("blender_disconnect", (blenderId) => {
    console.log("blender_disconnect: ", blenderId);

    if (connectedClients[blenderId]) {
      delete connectedClients[blenderId];
      removeMessageElement(blenderId);
    }
  });

  // Listen for messages from the server
  socket.on("blender_data", (data) => {
    blenderId = data["blenderId"];
    message = data["data"]["IFC_File"];

    console.log(data);

    if (connectedClients[blenderId] == true) {
      updateMessageElement(blenderId, message);
    } else {
      connectedClients[blenderId] = true;
      addMessageElement(blenderId, message);
    }
  });
});
