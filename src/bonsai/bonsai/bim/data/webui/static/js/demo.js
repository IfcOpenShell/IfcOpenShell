// A global variable to hold the WebSocket connection
let socket;

// Document ready function
// This function is triggered once the DOM is fully loaded.
// It sets the theme for the UI and
// establishes the WebSocket connection by calling connectSocket().
$(document).ready(function () {
  var defaultTheme = "blender"; // Default theme to be applied
  var theme = localStorage.getItem("theme") || defaultTheme; // Retrieve the stored theme or use the default
  setTheme(theme); // Apply the theme

  connectSocket();
});

// Function to establish WebSocket connection
// This function constructs the WebSocket connection URL using the SOCKET_PORT variable
// and initializes the socket connection. It also registers event handlers to listen
// for various events emitted by the server, such as 'blender_connect', 'blender_disconnect',
// 'theme_data', and 'demo_data'.
function connectSocket() {
  const url = "ws://localhost:" + SOCKET_PORT + "/web";
  socket = io(url);
  console.log("socket: ", socket);

  // Register socket event handlers
  socket.on("blender_connect", handleBlenderConnect);
  socket.on("blender_disconnect", handleBlenderDisconnect);
  socket.on("theme_data", handleThemeData);
  socket.on("demo_data", handleDemoData);
}

// Function to handle 'blender_connect' event
// This function is triggered when a new Bonsai instance connects to the server.
// The 'blenderId' is a unique identifier assigned by the server to each Bonsai instance.
// It helps distinguish between different instances of Bonsai connected to the server.
// The 'blenderId' is used in various parts of the code to ensure that messages and data
// are correctly associated with the appropriate Bonsai instance.
function handleBlenderConnect(blenderId) {
  console.log("blender connected: ", blenderId);
}

// Function to handle 'blender_disconnect' event
// This function is triggered when a Bonsai instance disconnects from the server.
// The 'blenderId' is used here to log which specific Bonsai instance has disconnected.
function handleBlenderDisconnect(blenderId) {
  console.log("blender disconnected: ", blenderId);
}

// Function to handle 'demo_data' event
// This function processes the demo data received from the server.
// It extracts the message and the Bonsai instance ID ('blenderId'),
// and updates the DOM to display the message. The 'blenderId' is used
// to differentiate between messages from different Bonsai instances.
// If the message for the specific Bonsai instance is already displayed, it updates the content;
// otherwise, it creates a new element to display the message.
function handleDemoData(demoData) {
  console.log(demoData);
  const message = demoData["data"]["demo_message"];
  const blenderId = demoData["blenderId"];
  const id = "message-" + blenderId;
  const messageHeader = $("#" + id);
  const messageText = `Bonsai instance with ID: ${blenderId} sent the message: ${message}`;

  if (messageHeader[0] === undefined) {
    const newMessageElement = $("<h3>", { id: id }).text(messageText);
    $("#message-container").prepend(newMessageElement);
  } else {
    messageHeader.text(messageText);
    messageHeader.prependTo("#message-container");
  }
}

// Function to send a message to the server
// This function is triggered when the user submits a message.
// It collects the message from the input field, constructs a message object,
// and emits the 'web_operator' event to the server with the message data.
// If 'blenderId' is specified, the message is sent to a specific Bonsai instance.
function sendMessage() {
  const inputMessage = $("#input-message").val();

  const msg = {
    sourcePage: "demo",
    // blenderId: BlenderId,  // specify the target Bonsai instance
    operator: {
      type: "message",
      message: inputMessage,
    },
  };
  socket.emit("web_operator", msg);
}

function handleThemeData(themeData) {
  // console.log(themeData);

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

  var styleElement = $("#demo-stylesheet")[0];
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

function toggleTheme() {
  if ($("html").hasClass("light")) {
    setTheme("dark");
  } else if ($("html").hasClass("dark")) {
    setTheme("blender");
  } else {
    setTheme("light");
  }
}
