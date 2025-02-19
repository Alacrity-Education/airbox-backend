require("dotenv").config();
const express = require("express");
const dataRoutes = require("./src/routes/data.routes");

const app = express();
app.use(express.json());

app.use("/api", dataRoutes);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
