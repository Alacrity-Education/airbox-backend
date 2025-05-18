const express = require("express");
const { insertData, getData, deleteData } = require("../controllers/dataController");

const router = express.Router();

router.post("/", insertData);
router.get("/", getData);
router.delete("/", deleteData);

module.exports = router;
