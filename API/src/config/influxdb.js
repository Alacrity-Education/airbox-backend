require("dotenv").config();
const { InfluxDB } = require("@influxdata/influxdb-client");

const INFLUX_URL = process.env.INFLUX_URL;
const INFLUX_TOKEN = process.env.INFLUX_TOKEN;
const INFLUX_ORG = process.env.INFLUX_ORG;
const INFLUX_BUCKET = process.env.INFLUX_BUCKET;

const influxDB = new InfluxDB({ url: INFLUX_URL, token: INFLUX_TOKEN });

module.exports = {
  influxDB,
  INFLUX_ORG,
  INFLUX_BUCKET,
};
