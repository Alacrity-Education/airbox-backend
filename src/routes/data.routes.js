const express = require("express");
const router = express.Router();
const { insertData, getData, deleteData } = require("../controllers/data.controller");

router.post("/data", insertData);
router.get("/data", getData);
router.delete("/data", deleteData);

module.exports = router;
