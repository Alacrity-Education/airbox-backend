const express = require("express");
const dataRoutes = require("./routes/dataRoutes");

const app = express();
app.use(express.json());

app.use("/data", dataRoutes);

module.exports = app;
