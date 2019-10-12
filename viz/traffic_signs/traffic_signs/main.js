const {
  app,
  BrowserWindow
} = require('electron');

let win;

app.on('ready', () => {
  // init window
  win = new BrowserWindow();
  win.maximize();
  win.loadURL('file://' + __dirname + '/index.html');
  // open developer console
  win.webContents.openDevTools();
})
